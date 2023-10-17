# Simple Log Visualization Tools

## Installation

```
pip install logtools
```

## Usage

### Merge by Timestamp

```
log-merge log1.log log2.log
```

### Merge by Timestamp Showing Aliases Instead of File Name

```
log-merge log1.log log2.log --aliases bootstrap codex21
```

### Merge and Filter by Timestamp

```
# If no timezone is provided, assumes UTC
log-merge log1.log log2.log --from 2021-01-01T00:00:00 --to 2021-01-02T00:00:00
```
