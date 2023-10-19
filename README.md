# Simple Log Visualization Tools

## Installation

```sh
pip install git+https://github.com/gmega/logtools.git
```

## Usage

### Merge by Timestamp

```sh
log-merge log1.log log2.log
```

### Merge by Timestamp Showing Aliases Instead of File Name

```sh
log-merge log1.log log2.log --aliases bootstrap codex21
```

### Merge and Filter by Timestamp

```sh
# If no timezone is provided, assumes UTC
log-merge log1.log log2.log --from 2021-01-01T00:00:00 --to 2021-01-02T00:00:00
```

### Transform Raw Logs into CSV

```sh
cat ./log1.log | log-to-csv
```

### Transform Raw Logs into CSV, Extracting Topics Into Column

```sh
cat ./log1.log | log-to-csv --extract-fields topics
```

