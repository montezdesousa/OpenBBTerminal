# THIS README IS A WORK IN PROGRESS

- [THIS README IS A WORK IN PROGRESS](#this-readme-is-a-work-in-progress)
  - [1. Introduction](#1-introduction)
  - [2. How to install?](#2-how-to-install)
    - [Git clone](#git-clone)
    - [Install](#install)
  - [3. How to add an extension?](#3-how-to-add-an-extension)
    - [Project](#project)
    - [Command](#command)
    - [Entrypoint](#entrypoint)
    - [Install extension](#install-extension)
  - [4. Usage](#4-usage)
  - [4.1 Static version](#41-static-version)
    - [4.1.1. Command output](#411-command-output)
      - [Helpers](#helpers)
    - [4.1.2. Utilities](#412-utilities)
      - [Settings](#settings)
      - [System](#system)
      - [Coverage](#coverage)
    - [4.1.3. OpenBB Hub Account](#413-openbb-hub-account)
  - [4.2 Dynamic version](#42-dynamic-version)
  - [5. REST API](#5-rest-api)
  - [5.1 Test users](#51-test-users)
  - [6. Front-end typing](#6-front-end-typing)

## 1. Introduction

This directory contains the OpenBB SDK's core functionality. It allows you to create an [extension](../../extensions/README.md) or a [provider](../../providers/README.md) that will be automatically turned into REST API endpoint and allow sharing data between commands.


## 2. How to install?

### Git clone

Git clone the repository:

```bash
git clone git@github.com:OpenBB-finance/OpenBBTerminal.git
```

### Install

Go to `openbb_sdk` folder and install the package.

```bash
cd openbb_sdk
poetry install
```

## 3. How to add an extension?

### Project

Build a Python package:

```bash
poetry new openbb-sdk-my_extension
```

### Command

Add a router and a command in the `openbb_sdk/extensions/<my_extension_folder>/<openbb_my_extension>/<my_extension>_router.py`

```python
from openbb_core.app.router import Router

router = Router(prefix="/router_name")

@router.command
def some_command(
    some_param: some_param_type,
) -> Obbject[Item]:
    pass
```

If your command only makes use of a standard model defined inside `openbb_provider/standard_models` directory, there is no need to repeat its structure in the parameters. Just pass the model name as an argument.

This is an example how we do it for `stocks.load` which only depends on `StockEOD` model defined in `openbb-provider`:

```python
@router.command(model="StockEOD")
def load(
    cc: CommandContext,                 # user settings inside
    provider_choices: ProviderChoices,  # available providers
    standard_params: StandardParams,    # symbol, start_date, etc.
    extra_params: ExtraParams,          # provider specific parameters
) -> Obbject[BaseModel]:
    """Load stock data for a specific ticker."""
    return Obbject(results=Query(**locals()).execute())
```

### Entrypoint

Add an entrypoint for the extension inside your `pyproject.toml` file.

```toml
packages = [{include = "openbb_sdk_my_extension"}]
...
[tool.poetry.extensions."openbb_extensions"]
extension_name_space = "my_extension.extension_router:router"
```

### Install extension

Install your extension.

```bash
cd openbb_sdk_my_extension
poetry install
```

## 4. Usage

Update your credentials and default providers by modifying the `.openbb_sdk/user_settings.json` inside your home directory:

```{json}
{
    "credentials": {
        "benzinga_api_key": null,
        "fmp_api_key": null,
        "polygon_api_key": null,
        "fred_api_key": null
    },
    "defaults": {
        "routes": {
            "/stocks/fa/balance": {
                "provider": "polygon"
            },
            "/stocks/load": {
                "provider": "fmp"
            },
            "/stocks/news": {
                "provider": "benzinga"
            }
        }
    }
}
```

Update your system settings by modifying the `.openbb_sdk/system_settings.json` file inside your home directory:


```{json}
{
    "run_in_isolation": null,
    "dbms_uri": null
}
```

## 4.1 Static version

Run your command:

```python
from openbb import obb

output = obb.stocks.load(
    symbol="TSLA",
    start_date="2023-01-01",
    provider="fmp",
    chart=True
    )
```

### 4.1.1. Command output

Each command will always return a  `Obbject`. There you will find:

- `results`: the data returned by the command `None`
- `provider`: the provider name (only available provider names allowed) used to get the data or `None`
- `warnings`: `List[Warning_]` with warnings caught during the command execution or `None`
- `error`: an `Error` with any exception that occurred during the command execution or `None`
- `chart`: a `Chart` with chart data and format or `None`

#### Helpers

To help you manipulate or visualize the data we make some helpers available.

- `to_dataframe`: transforms `results` into a pandas DataFrame

```python
>>> output.to_dataframe()
              open    high       low   close   adj_close    ...
date
2023-07-21  268.00  268.00  255.8000  260.02  260.019989    ...
2023-07-20  279.56  280.93  261.2000  262.90  262.899994    ...
2023-07-19  296.04  299.29  289.5201  291.26  291.260010    ...
```

- `to_dict`: transforms `results` into a dict of lists

```python
>>> output.to_dict()
{
    'open': [268.0, 279.56, 296.04],
    'high': [268.0, 280.93, 299.29],
    'low': [255.8, 261.2, 289.5201],
    'close': [260.02, 262.9, 291.26],
    'adj_close': [260.019989, 262.899994, 291.26001],
    ...
}
```

- `show`: displays `chart.content` to a chart

```python
>>> output.show()
# Jupyter Notebook: inline chart
# Python Interpreter: opens a PyWry window with the chart
```

- `to_plotly_json`: proxy to `chart.content`

```python
>>> output.to_plotly_json()
{
    'data':[
        {
            'close': [260.02, 262.9, 291.26],
            'decreasing': {'line': {'width': 1.1}},
            'high': [268.0, 280.93, 299.29],
            'increasing': {'line': {'width': 1.1}},
            ...
        }
    ...
    ]
}
```

### 4.1.2. Utilities

#### Settings

These are your user settings, you can change them anytime and they will be applied. Don't forget to `sdk.account.save()` if you want these changes to persist.

```python
from openbb import obb

obb.settings.profile
obb.settings.credentials
obb.settings.preferences
obb.settings.defaults
```

#### System

Check your system settings. Most of the properties are read-only during runtime.

- `debug_mode`: Setting it as `True` will immediately raise all occurring exceptions.

```python
from openbb import obb

obb.system
```

#### Coverage

Obtain the coverage of providers and commands.

```python
>>> obb.coverage.commands
{
    '/crypto/load': ['fmp', 'polygon'],
    '/economy/const': ['fmp'],
    '/economy/cpi': ['fred'],
    ...
}
```

```python
>>> obb.coverage.providers
{
    'fmp':
    [
        '/crypto/load',
        '/economy/const',
        '/economy/index',
        ...
    ],
    'fred': ['/economy/cpi'],
    ...
}
```

### 4.1.3. OpenBB Hub Account

You can login to your OpenBB Hub account and save your credentials there to access them from any device.

```python
from openbb import obb

# Login with email, password or SDK token
obb.account.login(email="your_email", password="your_password", remember_me=True)  # pragma: allowlist secret

# Change a credential
obb.account.settings.credentials.polygon_api_key = "new_key"  # pragma: allowlist secret

# Save account changes
obb.account.save()

# Refresh account with latest changes
obb.account.refresh()

# Logout
obb.account.logout()
```

## 4.2 Dynamic version

You can also use the dynamic version to consume the API endpoints from Python itself.

In fact, the static version makes use of this feature to run each command. Take a look at the example below:

```python
>>> from openbb_core.app.command_runner import CommandRunnerSession
>>> crs = CommandRunnerSession()
>>> response = crs.run(
             "/stocks/load",
             provider_choices={
                 "provider": "fmp",
             },
             standard_params={
                 "symbol": "TSLA",
                 "start_date": "2023-07-01",
                 "end_date": "2023-07-25",
             },
             extra_params={},
             chart=True,
         )
>>> response
JournalEntry

id: ...                 # UUID Tag
arguments: ...          # Arguments of the command.
duration ...            # Execution duration in nano second of the command.
output ...              # Output of the command.
route: "/stocks/load"   # Route of the command.
timestamp: ...          # Execution starting timestamp.
alias_list: ...         # List of alias to find a JournalEntry easier than with it's `tag`.

>>> response.output
Obbject

id: ...                 # UUID Tag
results: ...            # Serializable results.
provider: ...           # Provider name.
warnings: ...           # List of warnings.
error: ...              # Exception caught.
chart: ...              # Chart object.
```

## 5. REST API

OpenBB SDK comes with a ready to use Rest API built with FastAPI. Start the application using this command:

```bash
uvicorn openbb_core.api.rest_api:app --reload
```

## 5.1 Test users

There are 2 default users for testing purpose:

User "openbb"

- username : openbb
- password : openbb

User "finance"

- username : finance
- password : finance

## 6. Front-end typing

Here are libraries to get frontend typing.

openapi-typescript + openapi-fetch

- <https://github.com/drwpow/openapi-typescript>

openapi-generator

- <https://fastapi.tiangolo.com/advanced/generate-clients/>