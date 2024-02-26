# dang-genius-crypto-ai

Trade crypto using AI

## Requirements

`conda` must be installed.

```
% conda --version
conda 23.9.0
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

```
# To create an environment, use
#
#     $ conda env create --name dg-3.12 --file environment.yml 
#
# To activate this environment, use
#
#     $ conda activate dg-3.11
#
# To deactivate an active environment, use
#
#     $ conda deactivate
```

### git with ssh

See: https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent

```
ssh-keygen -t ed25519 -C "your@email.com"
eval `ssh-agent`
ssh-add
```

### coinbase setup

See:
https://developers.coinbase.com/api/v2
https://developers.coinbase.com/docs/wallet/notifications
https://www.coinbase.com/settings/api

```
NOTE: API keys give direct access to your account, so be sure to protect them.
Never share your keys with anyone, and store them only in secure places.
Connecting your keys to 3rd-party websites could compromise your account security.
```

Create a file named `.env`. In that file put the API key and secret.

```
cat ./.env
export CB-API-KEY=Put-your-real-key-here
export CB-API-SECRET=Put-your-real-secret-here
```

To check your coinbase API connection:
`python ./coinbase-check.py`


### dang_genius package

```
 python -c 'from dang_genius.wallet import wallet_summary as ws; print(ws())'
 python -c 'from dang_genius.market import market_check as mc; mc()'
```

### TODO: 
pip install pycaret[full]
