# dang-genius-crypto-ai
Trade crypto using AI



## Requirements

`conda` must be installed.

```
% conda --version
conda 23.5.2
```

Use `brew` to install and upgrade conda:

```
% brew install miniconda
% brew upgrade miniconda
```

### Optional Tools:

```
% brew install nano
% brew install git
% brew install tree
```

`export PATH=/opt/homebrew/Cellar:$PATH`

## Environment

`conda create -y --name dg-3.10 python=3.10`

`
# To activate this environment, use
#
#     $ conda activate dg-3.10
#
# To deactivate an active environment, use
#
#     $ conda deactivate
`

### git with ssh

```
# See: https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent
ssh-keygen -t ed25519 -C "your@email.com"
eval `ssh-agent`
ssh-add
```
