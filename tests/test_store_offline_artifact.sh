#!/usr/bin/env bash
# Behavioral checks for offline CI artifact storage.
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
SCRIPT="${ROOT_DIR}/.github/scripts/store-offline-artifact.sh"
WORKFLOW="${ROOT_DIR}/.github/workflows/legal-index.yml"
README="${ROOT_DIR}/README.md"

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

assert_eq() {
  local got=$1 expected=$2 label=$3
  if [[ "$got" != "$expected" ]]; then
    fail "${label}: expected [${expected}] got [${got}]"
  fi
}

assert_file() {
  local path=$1 content=$2
  [[ -f "$path" ]] || fail "missing file $path"
  assert_eq "$(cat "$path")" "$content" "$path"
}

run_store() {
  local out_file=$1
  local log_file=$2
  shift 2
  set +e
  "$@" bash "$SCRIPT" >"$log_file" 2>&1
  local status=$?
  set -e
  printf '%s' "$status" > "${out_file}.status"
}

REPO=anizalani/legalindexer
RUN_ID=424242
ATTEMPT=1
JOB=generate-index
REL="${REPO}/${RUN_ID}/${ATTEMPT}/${JOB}"

# Workflow contract: offline path skips upload; fallback keeps a 3-day upload.
grep -q 'store-offline-artifact.sh' "$WORKFLOW" || fail "workflow does not call the offline store script"
grep -q "steps.offline_artifacts.outputs.offline != 'true'" "$WORKFLOW" || fail "upload step is not conditional"
grep -q 'retention-days: 3' "$WORKFLOW" || fail "fallback retention is not 3 days"
if grep -q 'retention-days: 30' "$WORKFLOW"; then
  fail "workflow still requests 30-day artifact retention"
fi
if grep -Eq 'delete-artifact|actions/delete-artifact|gh api .*artifacts' "$WORKFLOW" "$SCRIPT"; then
  fail "workflow deletes existing artifacts"
fi
grep -q 'Output file was not created' "$WORKFLOW" || fail "output verification check was removed"
grep -q '/mnt/user/ci-artifacts' "$README" || fail "README does not document the runner mount"
grep -q 'CI_ARTIFACT_ROOT' "$README" || fail "README does not document CI_ARTIFACT_ROOT"

# The store script must not dump the environment or enable trace logging.
if grep -Eq 'set -x|printenv|declare -p|env \|' "$SCRIPT"; then
  fail "store script can print the environment"
fi

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

source_file="${tmp}/legal_index.txt"
printf 'NEW INDEX\n' > "$source_file"
chmod 640 "$source_file"

# --- success: env root, siblings and older runs stay, mode is preserved ---
root="${tmp}/ci-artifacts"
mkdir -p "${root}/anizalani/legalindexer/999/1/generate-index"
older="${root}/anizalani/legalindexer/999/1/generate-index/legal_index.txt"
printf 'OLDER\n' > "$older"
job_dir="${root}/${REL}"
mkdir -p "$job_dir"
printf 'KEEP\n' > "${job_dir}/keep.txt"
printf 'PREVIOUS\n' > "${job_dir}/other.txt"

github_output="${tmp}/github_output_ok"
log="${tmp}/log_ok"
: > "$github_output"
run_store "$github_output" "$log" \
  env \
  GITHUB_OUTPUT="$github_output" \
  CI_ARTIFACT_ROOT="$root" \
  CI_ARTIFACT_ROOT_VAR="" \
  OUTPUT_FILE="$source_file" \
  ARTIFACT_REPO="$REPO" \
  ARTIFACT_RUN_ID="$RUN_ID" \
  ARTIFACT_ATTEMPT="$ATTEMPT" \
  ARTIFACT_JOB="$JOB" \
  GITHUB_TOKEN="ghs_supersecret_token" \
  MY_SECRET="hunter2-do-not-print"
assert_eq "$(cat "${github_output}.status")" "0" "success exit"
assert_eq "$(cat "$github_output")" "offline=true" "success output"
assert_file "${job_dir}/legal_index.txt" "NEW INDEX"
assert_file "${job_dir}/keep.txt" "KEEP"
assert_file "${job_dir}/other.txt" "PREVIOUS"
assert_file "$older" "OLDER"
mode=$(stat -c '%a' "${job_dir}/legal_index.txt")
assert_eq "$mode" "640" "preserved mode"
if grep -q "$root" "$log" || grep -q 'ghs_supersecret_token' "$log" || grep -q 'hunter2-do-not-print' "$log"; then
  fail "success log printed the artifact root or a secret"
fi
grep -q "CI_ARTIFACT_ROOT/${REL}/legal_index.txt" "$log" || fail "success log missing relative layout"
grep -q 'Skipping GitHub artifact upload' "$log" || fail "success log does not record the skipped upload"

# --- Actions variable overrides the runner environment ---
root_var="${tmp}/from-var"
root_env="${tmp}/from-env"
mkdir -p "$root_var" "$root_env"
printf 'KEEPENV\n' > "${root_env}/keep.txt"
github_output="${tmp}/github_output_var"
log="${tmp}/log_var"
: > "$github_output"
run_store "$github_output" "$log" \
  env \
  GITHUB_OUTPUT="$github_output" \
  CI_ARTIFACT_ROOT_VAR="${root_var}/" \
  CI_ARTIFACT_ROOT="$root_env" \
  OUTPUT_FILE="$source_file" \
  ARTIFACT_REPO="$REPO" \
  ARTIFACT_RUN_ID="$RUN_ID" \
  ARTIFACT_ATTEMPT="$ATTEMPT" \
  ARTIFACT_JOB="$JOB"
assert_eq "$(cat "$github_output")" "offline=true" "var override output"
assert_file "${root_var}/${REL}/legal_index.txt" "NEW INDEX"
[[ ! -e "${root_env}/${REL}/legal_index.txt" ]] || fail "runner env root was used even though the Actions variable was set"
assert_file "${root_env}/keep.txt" "KEEPENV"

# --- whitespace-only Actions variable falls through to the runner env ---
github_output="${tmp}/github_output_ws"
log="${tmp}/log_ws"
: > "$github_output"
run_store "$github_output" "$log" \
  env \
  GITHUB_OUTPUT="$github_output" \
  CI_ARTIFACT_ROOT_VAR="   " \
  CI_ARTIFACT_ROOT="$root" \
  OUTPUT_FILE="$source_file" \
  ARTIFACT_REPO="$REPO" \
  ARTIFACT_RUN_ID="$RUN_ID" \
  ARTIFACT_ATTEMPT="$ATTEMPT" \
  ARTIFACT_JOB="$JOB"
assert_eq "$(cat "$github_output")" "offline=true" "whitespace var falls through"

# --- unset root does not create a directory and does not delete an archive ---
archive="${tmp}/archive"
mkdir -p "$archive"
printf 'STILLHERE\n' > "${archive}/kept.txt"
github_output="${tmp}/github_output_unset"
log="${tmp}/log_unset"
: > "$github_output"
(
  cd "$tmp"
  run_store "$github_output" "$log" \
    env \
    GITHUB_OUTPUT="$github_output" \
    CI_ARTIFACT_ROOT_VAR="" \
    CI_ARTIFACT_ROOT="" \
    OUTPUT_FILE="$source_file" \
    ARTIFACT_REPO="$REPO" \
    ARTIFACT_RUN_ID="$RUN_ID" \
    ARTIFACT_ATTEMPT="$ATTEMPT" \
    ARTIFACT_JOB="$JOB"
)
assert_eq "$(cat "${github_output}.status")" "0" "unset exit"
assert_eq "$(cat "$github_output")" "offline=false" "unset output"
assert_file "${archive}/kept.txt" "STILLHERE"
[[ ! -d "${tmp}/anizalani" ]] || fail "unset root created a repo directory in the workspace"

# --- relative path is not used and is not created ---
github_output="${tmp}/github_output_rel"
log="${tmp}/log_rel"
: > "$github_output"
(
  cd "$tmp"
  run_store "$github_output" "$log" \
    env \
    GITHUB_OUTPUT="$github_output" \
    CI_ARTIFACT_ROOT="relative/ci-artifacts" \
    OUTPUT_FILE="$source_file" \
    ARTIFACT_REPO="$REPO" \
    ARTIFACT_RUN_ID="$RUN_ID" \
    ARTIFACT_ATTEMPT="$ATTEMPT" \
    ARTIFACT_JOB="$JOB"
)
assert_eq "$(cat "$github_output")" "offline=false" "relative output"
[[ ! -e "${tmp}/relative" ]] || fail "relative CI_ARTIFACT_ROOT was created"

# --- missing root directory is not created ---
missing="${tmp}/missing-mount"
github_output="${tmp}/github_output_missing"
log="${tmp}/log_missing"
: > "$github_output"
run_store "$github_output" "$log" \
  env \
  GITHUB_OUTPUT="$github_output" \
  CI_ARTIFACT_ROOT="$missing" \
  OUTPUT_FILE="$source_file" \
  ARTIFACT_REPO="$REPO" \
  ARTIFACT_RUN_ID="$RUN_ID" \
  ARTIFACT_ATTEMPT="$ATTEMPT" \
  ARTIFACT_JOB="$JOB"
assert_eq "$(cat "$github_output")" "offline=false" "missing mount output"
[[ ! -e "$missing" ]] || fail "missing CI_ARTIFACT_ROOT was created"

# --- root exists but is a file ---
root_file="${tmp}/not-a-dir"
printf 'x\n' > "$root_file"
github_output="${tmp}/github_output_file"
log="${tmp}/log_file"
: > "$github_output"
run_store "$github_output" "$log" \
  env \
  GITHUB_OUTPUT="$github_output" \
  CI_ARTIFACT_ROOT="$root_file" \
  OUTPUT_FILE="$source_file" \
  ARTIFACT_REPO="$REPO" \
  ARTIFACT_RUN_ID="$RUN_ID" \
  ARTIFACT_ATTEMPT="$ATTEMPT" \
  ARTIFACT_JOB="$JOB"
assert_eq "$(cat "$github_output")" "offline=false" "file root output"
assert_file "$root_file" "x"

# --- symlink inside the root is not followed and is not removed ---
outside="${tmp}/outside"
mkdir -p "$outside"
printf 'OUTSIDE\n' > "${outside}/kept.txt"
link_root="${tmp}/link-root"
mkdir -p "$link_root"
ln -s "$outside" "${link_root}/anizalani"
github_output="${tmp}/github_output_link"
log="${tmp}/log_link"
: > "$github_output"
run_store "$github_output" "$log" \
  env \
  GITHUB_OUTPUT="$github_output" \
  CI_ARTIFACT_ROOT="$link_root" \
  OUTPUT_FILE="$source_file" \
  ARTIFACT_REPO="$REPO" \
  ARTIFACT_RUN_ID="$RUN_ID" \
  ARTIFACT_ATTEMPT="$ATTEMPT" \
  ARTIFACT_JOB="$JOB"
assert_eq "$(cat "$github_output")" "offline=false" "symlink output"
[[ -L "${link_root}/anizalani" ]] || fail "pre-existing symlink was removed"
assert_file "${outside}/kept.txt" "OUTSIDE"
[[ ! -e "${outside}/legalindexer" ]] || fail "write escaped through a symlink"

# --- artifact root itself may be a symlink to the mounted share ---
real_share="${tmp}/real-share"
mkdir -p "$real_share"
link_parent="${tmp}/runner-mnt"
mkdir -p "$link_parent"
ln -s "$real_share" "${link_parent}/ci-artifacts"
github_output="${tmp}/github_output_mountlink"
log="${tmp}/log_mountlink"
: > "$github_output"
run_store "$github_output" "$log" \
  env \
  GITHUB_OUTPUT="$github_output" \
  CI_ARTIFACT_ROOT="${link_parent}/ci-artifacts" \
  OUTPUT_FILE="$source_file" \
  ARTIFACT_REPO="$REPO" \
  ARTIFACT_RUN_ID="$RUN_ID" \
  ARTIFACT_ATTEMPT="$ATTEMPT" \
  ARTIFACT_JOB="$JOB"
assert_eq "$(cat "$github_output")" "offline=true" "symlinked mount output"
assert_file "${real_share}/${REL}/legal_index.txt" "NEW INDEX"

# --- parent path with .. is refused ---
github_output="${tmp}/github_output_dotdot"
log="${tmp}/log_dotdot"
: > "$github_output"
run_store "$github_output" "$log" \
  env \
  GITHUB_OUTPUT="$github_output" \
  CI_ARTIFACT_ROOT="${tmp}/ci-artifacts/../../tmp" \
  OUTPUT_FILE="$source_file" \
  ARTIFACT_REPO="$REPO" \
  ARTIFACT_RUN_ID="$RUN_ID" \
  ARTIFACT_ATTEMPT="$ATTEMPT" \
  ARTIFACT_JOB="$JOB"
assert_eq "$(cat "$github_output")" "offline=false" "dotdot root output"

# --- missing output file fails closed and leaves existing artifacts ---
github_output="${tmp}/github_output_absent"
log="${tmp}/log_absent"
: > "$github_output"
run_store "$github_output" "$log" \
  env \
  GITHUB_OUTPUT="$github_output" \
  CI_ARTIFACT_ROOT="$root" \
  OUTPUT_FILE="${tmp}/does-not-exist.txt" \
  ARTIFACT_REPO="$REPO" \
  ARTIFACT_RUN_ID="$RUN_ID" \
  ARTIFACT_ATTEMPT="$ATTEMPT" \
  ARTIFACT_JOB="$JOB"
assert_eq "$(cat "${github_output}.status")" "1" "missing output exit"
assert_file "$older" "OLDER"
assert_file "${job_dir}/keep.txt" "KEEP"
if grep -q '^offline=' "$github_output"; then
  fail "missing output file still wrote an offline result"
fi

# --- filenames with spaces stay a single path segment ---
spaced="${tmp}/legal index.txt"
printf 'SPACED\n' > "$spaced"
chmod 644 "$spaced"
github_output="${tmp}/github_output_space"
log="${tmp}/log_space"
: > "$github_output"
run_store "$github_output" "$log" \
  env \
  GITHUB_OUTPUT="$github_output" \
  CI_ARTIFACT_ROOT="$root" \
  OUTPUT_FILE="$spaced" \
  ARTIFACT_REPO="$REPO" \
  ARTIFACT_RUN_ID="7" \
  ARTIFACT_ATTEMPT="2" \
  ARTIFACT_JOB="$JOB"
assert_eq "$(cat "$github_output")" "offline=true" "spaced name output"
assert_file "${root}/${REPO}/7/2/${JOB}/legal index.txt" "SPACED"
assert_file "${job_dir}/keep.txt" "KEEP"

echo "ok"
