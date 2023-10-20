set -e

base_folder=${1:-"./data/20"}
mkdir -p "${base_folder}/pods/uploads"

# tags uploads with id
for i in "${base_folder}"/pods/codex-continuous-tests-0codex*; do
  python -m adhoc.identify_uploads < "$i" > "${i%/*}/uploads/${i##*/}"
done

# transforms raw logs into single CSV
for i in "${base_folder}"/pods/uploads/codex-continuous-tests-0codex*; do
  python -m logtools.cli.to_csv < "$i" \
  --extract-fields upload \
  --constant-column \
  source=${${i##*/}%.*} >> "${base_folder}"/pods/uploads/all_uploads.csv.temp
done

./bin/csv-concat.sh < "${base_folder}"/pods/uploads/all_uploads.csv.temp > "${base_folder}"/pods/uploads/all_uploads.csv
rm "${base_folder}"/pods/uploads/all_uploads.csv.temp

# extracts debug endpoint data and looks into wantlist sizes
grep -h 'Before upload\|After download' "${base_folder}"/runner/*.log | \
 sed -E 's/\[(.{28})\] <([A-Z]+[0-9]+)> (Before upload|After download): (.*)$/\4/p' > "${base_folder}"/runner/merged.jsonl

jq '.pendingBlocks' < "${base_folder}"/runner/merged.jsonl | uniq # should print 0