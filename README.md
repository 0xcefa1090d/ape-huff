# ape-huff

Huff compiler plugin for the eth-ape development framework

## Dependencies

To build binaries from source when a pre-built binary isn't available the build tool `cargo` must be installed. Refer to the `cargo`
[documentation](https://doc.rust-lang.org/cargo/) for instruction on installing it.

## Installation

```bash
$ pip install ape-huff
```

## Usage

To use the `ape-huff` plugin simply include huff contracts (files with the `.huff` extension) in your project's `contracts/` directory.

### Selecting a Version

By default `ape-huff` will use the latest stable huff release to compile contracts. To customize the version used
update your `ape-config.yaml` to include the following:

```yaml
huff:
  version: 0.3.1
```
