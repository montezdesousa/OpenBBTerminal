# OpenBB Excel Add-in

This folder contains the relevant artifacts to import some functionality of OpenBB SDK in Microsof Excel. 

The add-in feature is to provide the DataFrames resulting from SDK commands.

Code is still very hacky... but it works :)

## Snapshot
![alt text](https://user-images.githubusercontent.com/79287829/219010018-f618b722-13b8-4dde-98f4-36ed21756cb0.png)

## How to setup?

There are 3 relevant pieces to make this work:
1. Excel add-in `openbb.xlam` is located in the folder "openbb_terminal/core/addin"
2. OpenBBTerminal.exe build from this branch
3. The dll located in "openbb_terminal\core\addin\dll". Choose the one appropriate for your architecture 32 (xlwings32-0.29.1.dll) or 64 bit (xlwings64-0.29.1.dll).

There are 2 steps that are only required the first time:
* Copy the "xlwings[XX]-0.29.1.dll" to "C:\Program Files\Microsoft Office\root\Office16" or whatever your Excel.exe lives
* Open Excel > File > Options > Go to tab Add-ins > Click on "Go..." > "Browse..." > Choose the location of `openbb.xlam`

Using the add-in:
1. Open the OpenBBTerminal.exe if you build it or run `python terminal.py`
2. Query the OpenBB SDK with `=OBB([query], [args])`

Note: It should be possible to launch the server by clicking "Launch COM server" icon on the OpenBB ribbon. To do that and avoiding step 1. of "Using the add-in" list you can open the VBA developer tools and change the path in the module "RibbonMyAddin" with the path to the OpenBBTerminal.exe
`Shell "cmd.exe /K [Full path to]\OpenBBTerminal.exe --server"`

Examples:
`=OBB("economy.events")`
`=OBB("stocks.fa.income", "TSLA")`
`=OBB("forex.load", "EUR", "USD", "d", "1day", "2023-01-01")`
