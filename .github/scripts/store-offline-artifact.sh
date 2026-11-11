#!/usr/bin/env bash
# Copy one CI output onto a local artifact root when that root is usable.
#
# Layout (under CI_ARTIFACT_ROOT):
#   <owner>/<repo>/<run_id>/<run_attempt>/<job>/<filename>
#
# CI_ARTIFACT_ROOT_VAR (Actions variable) wins when it is non-empty.
# Otherwise CI_ARTIFACT_ROOT from the runner environment is used.
#
# Writes a single offline=true or offline=false line to GITHUB_OUTPUT.
# Removes only the temporary file created during this attempt.
# Does not delete stored artifacts, sibling files, or the artifact root.

set -euo pipefail

if [[ -z "${GITHUB_OUTPUT:-}" ]]; then
  echo "GITHUB_OUTPUT is not set." >&2
  exit 1
fi

write_offline() {
  printf 'offline=%s\n' "$1" >> "$GITHUB_OUTPUT"
}

if [[ -z "${OUTPUT_FILE:-}" || ! -f "$OUTPUT_FILE" ]]; then
  echo "Output file is missing; refusing to store or upload an empty artifact." >&2
  exit 1
fi

base=$(basename -- "$OUTPUT_FILE")
if [[ -z "$base" || "$base" == "." || "$base" == ".." || "$base" == */* || "$base" == *\\* || "$base" == *$'\n'* || "$base" == *$'\r'* ]]; then
  echo "Output filename is not a single path segment." >&2
  exit 1
fi

trim_root() {
  root="${root#"${root%%[![:space:]]*}"}"
  root="${root%"${root##*[![:space:]]}"}"
  while [[ -n "$root" && "$root" == */ && "$root" != "/" ]]; do
    root="${root%/}"
  done
}

# Actions variable wins. A blank value falls through to the runner environment.
root="${CI_ARTIFACT_ROOT_VAR:-}"
trim_root
if [[ -z "$root" ]]; then
  root="${CI_ARTIFACT_ROOT:-}"
  trim_root
fi

repo="${ARTIFACT_REPO:-}"
run_id="${ARTIFACT_RUN_ID:-}"
attempt="${ARTIFACT_ATTEMPT:-}"
job="${ARTIFACT_JOB:-}"

owner="${repo%%/*}"
name="${repo#*/}"
valid_layout=true
if [[ "$repo" != */* || "$repo" == */*/* || -z "$owner" || -z "$name" || "$owner" == "." || "$owner" == ".." || "$name" == "." || "$name" == ".." ]]; then
  valid_layout=false
fi
if [[ "$owner" == */* || "$owner" == *\\* || "$owner" == *$'\n'* || "$owner" == *$'\r'* ]]; then
  valid_layout=false
fi
if [[ "$name" == */* || "$name" == *\\* || "$name" == *$'\n'* || "$name" == *$'\r'* ]]; then
  valid_layout=false
fi
case "$run_id" in
  ''|*[!0-9]*) valid_layout=false ;;
esac
case "$attempt" in
  ''|*[!0-9]*) valid_layout=false ;;
esac
case "$job" in
  [A-Za-z_][A-Za-z0-9_-]*) ;;
  *) valid_layout=false ;;
esac

if [[ "$valid_layout" != true ]]; then
  echo "Artifact layout values are unusable. Falling back to a short-lived GitHub artifact." >&2
  write_offline false
  exit 0
fi

use_offline=false
dest=""

root_unusable() {
  case "$root" in
    ""|"/") return 0 ;;
  esac
  if [[ "$root" == *$'\n'* || "$root" == *$'\r'* || "$root" == *\\* ]]; then
    return 0
  fi
  [[ "$root" == /* ]] || return 0
  IFS=/ read -ra root_parts <<< "$root"
  local part
  for part in "${root_parts[@]}"; do
    if [[ "$part" == "." || "$part" == ".." ]]; then
      return 0
    fi
  done
  return 1
}

if [[ -z "$root" ]]; then
  echo "CI_ARTIFACT_ROOT is not set. Falling back to a short-lived GitHub artifact."
elif root_unusable; then
  echo "CI_ARTIFACT_ROOT cannot be used. Falling back to a short-lived GitHub artifact."
elif [[ ! -d "$root" || ! -w "$root" ]]; then
  echo "CI_ARTIFACT_ROOT is not a writable directory. Falling back to a short-lived GitHub artifact."
else
  dest="$root"
  layout_ok=true
  for part in "$owner" "$name" "$run_id" "$attempt" "$job"; do
    dest="${dest}/${part}"
    if [[ -L "$dest" ]]; then
      layout_ok=false
      break
    fi
    if [[ ! -e "$dest" ]]; then
      if ! mkdir -- "$dest" >/dev/null 2>&1; then
        layout_ok=false
        break
      fi
    fi
    if [[ -L "$dest" || ! -d "$dest" || ! -w "$dest" ]]; then
      layout_ok=false
      break
    fi
  done

  if [[ "$layout_ok" == true ]]; then
    root_real=$(readlink -f -- "$root" 2>/dev/null || true)
    dest_real=$(readlink -f -- "$dest" 2>/dev/null || true)
    if [[ -n "$root_real" && -n "$dest_real" && "$dest_real" == "$root_real"/* ]]; then
      use_offline=true
    else
      echo "Artifact destination is outside CI_ARTIFACT_ROOT. Falling back to a short-lived GitHub artifact."
    fi
  else
    echo "CI_ARTIFACT_ROOT is not writable. Falling back to a short-lived GitHub artifact."
  fi
fi

if [[ "$use_offline" == true ]]; then
  tmp=$(mktemp "${dest}/.partial.XXXXXX" 2>/dev/null) || true
  copied=false
  if [[ -n "${tmp:-}" && -f "$tmp" ]]; then
    if cp -f -- "$OUTPUT_FILE" "$tmp" >/dev/null 2>&1 && cmp -s -- "$OUTPUT_FILE" "$tmp"; then
      if [[ -e "${dest}/${base}" && ! -f "${dest}/${base}" ]]; then
        :
      elif mv -f -- "$tmp" "${dest}/${base}" >/dev/null 2>&1; then
        chmod --reference="$OUTPUT_FILE" -- "${dest}/${base}" >/dev/null 2>&1 || chmod 644 -- "${dest}/${base}" >/dev/null 2>&1 || true
        copied=true
      fi
    fi
    if [[ "$copied" != true && -f "$tmp" ]]; then
      case "$(basename -- "$tmp")" in
        .partial.*) rm -f -- "$tmp" ;;
      esac
    fi
  fi

  if [[ "$copied" == true && -f "${dest}/${base}" ]] && cmp -s -- "$OUTPUT_FILE" "${dest}/${base}"; then
    write_offline true
    echo "Stored CI output under CI_ARTIFACT_ROOT/${repo}/${run_id}/${attempt}/${job}/${base}. Skipping GitHub artifact upload."
    exit 0
  fi
  echo "Could not store the CI output offline. Falling back to a short-lived GitHub artifact."
fi

write_offline false
