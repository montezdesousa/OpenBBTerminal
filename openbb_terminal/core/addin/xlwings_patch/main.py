class Range:
    """
    Returns a Range object that represents a cell or a range of cells.

    Arguments
    ---------
    cell1 : str or tuple or Range
        Name of the range in the upper-left corner in A1 notation or as index-tuple or
        as name or as xw.Range object. It can also specify a range using the range
        operator (a colon), .e.g. 'A1:B2'

    cell2 : str or tuple or Range, default None
        Name of the range in the lower-right corner in A1 notation or as index-tuple or
        as name or as xw.Range object.

    Examples
    --------

    .. code-block:: python

        import xlwings as xw
        sheet1 = xw.Book("MyBook.xlsx").sheets[0]

        sheet1.range("A1")
        sheet1.range("A1:C3")
        sheet1.range((1,1))
        sheet1.range((1,1), (3,3))
        sheet1.range("NamedRange")

        # Or using index/slice notation
        sheet1["A1"]
        sheet1["A1:C3"]
        sheet1[0, 0]
        sheet1[0:4, 0:4]
        sheet1["NamedRange"]
    """

    def __init__(self, cell1=None, cell2=None, **options):
        # Arguments
        impl = options.pop("impl", None)
        if impl is None:
            if (
                cell2 is not None
                and isinstance(cell1, Range)
                and isinstance(cell2, Range)
            ):
                if cell1.sheet != cell2.sheet:
                    raise ValueError("Ranges are not on the same sheet")
                impl = cell1.sheet.range(cell1, cell2).impl
            elif cell2 is None and isinstance(cell1, str):
                impl = apps.active.range(cell1).impl
            elif cell2 is None and isinstance(cell1, tuple):
                impl = sheets.active.range(cell1, cell2).impl
            elif (
                cell2 is not None
                and isinstance(cell1, tuple)
                and isinstance(cell2, tuple)
            ):
                impl = sheets.active.range(cell1, cell2).impl
            else:
                raise ValueError("Invalid arguments")

        self._impl = impl

        # Keyword Arguments
        self._impl.options = options
        self._options = options

    @property
    def impl(self):
        return self._impl

    @property
    def api(self):
        """
        Returns the native object (``pywin32`` or ``appscript`` obj)
        of the engine being used.

        .. versionadded:: 0.9.0
        """
        return self.impl.api

    def __eq__(self, other):
        return (
            isinstance(other, Range)
            and self.sheet == other.sheet
            and self.row == other.row
            and self.column == other.column
            and self.shape == other.shape
        )

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.sheet, self.row, self.column, self.shape))

    def __iter__(self):
        # Iterator object that returns cell Ranges: (1, 1), (1, 2) etc.
        for i in range(len(self)):
            yield self(i + 1)

    def options(self, convert=None, **options):
        """
        Allows you to set a converter and their options. Converters define how Excel
        Ranges and their values are being converted both during reading and writing
        operations. If no explicit converter is specified, the base converter is being
        applied, see :ref:`converters`.

        Arguments
        ---------
        ``convert`` : object, default None
            A converter, e.g. ``dict``, ``np.array``, ``pd.DataFrame``, ``pd.Series``,
            defaults to default converter

        Keyword Arguments
        -----------------
        ndim : int, default None
            number of dimensions

        numbers : type, default None
            type of numbers, e.g. ``int``

        dates : type, default None
            e.g. ``datetime.date`` defaults to ``datetime.datetime``

        empty : object, default None
            transformation of empty cells

        transpose : Boolean, default False
            transpose values

        expand : str, default None
            One of ``'table'``, ``'down'``, ``'right'``

        chunksize : int
            Use a chunksize, e.g. ``10000`` to prevent timeout or memory issues when
            reading or writing large amounts of data. Works with all formats, including
            DataFrames, NumPy arrays, and list of lists.

        err_to_str : Boolean, default False
            If ``True``, will include cell errors such as ``#N/A`` as strings. By
            default, they will be converted to ``None``.

            .. versionadded:: 0.28.0

        => For converter-specific options, see :ref:`converters`.

        Returns
        -------
        Range object

        """
        options["convert"] = convert
        return Range(impl=self.impl, **options)

    @property
    def sheet(self):
        """
        Returns the Sheet object to which the Range belongs.

        .. versionadded:: 0.9.0
        """
        return Sheet(impl=self.impl.sheet)

    def __len__(self):
        return len(self.impl)

    @property
    def count(self):
        """
        Returns the number of cells.

        """
        return len(self)

    @property
    def row(self):
        """
        Returns the number of the first row in the specified range. Read-only.

        Returns
        -------
        Integer


        .. versionadded:: 0.3.5
        """
        return self.impl.row

    @property
    def column(self):
        """
        Returns the number of the first column in the in the specified range. Read-only.

        Returns
        -------
        Integer


        .. versionadded:: 0.3.5
        """
        return self.impl.column

    @property
    def raw_value(self):
        """
        Gets and sets the values directly as delivered from/accepted by the engine that
        s being used (``pywin32`` or ``appscript``) without going through any of
        xlwings' data cleaning/converting. This can be helpful if speed is an issue but
        naturally will be engine specific, i.e. might remove the cross-platform
        compatibility.
        """
        return self.impl.raw_value

    @raw_value.setter
    def raw_value(self, data):
        self.impl.raw_value = data

    def clear_contents(self):
        """Clears the content of a Range but leaves the formatting."""
        return self.impl.clear_contents()

    def clear_formats(self):
        """Clears the format of a Range but leaves the content.

        .. versionadded:: 0.26.2
        """
        return self.impl.clear_formats()

    def clear(self):
        """Clears the content and the formatting of a Range."""
        return self.impl.clear()

    @property
    def has_array(self):
        """
        ``True`` if the range is part of a legacy CSE Array formula
        and ``False`` otherwise.
        """
        return self.impl.has_array

    def end(self, direction):
        """
        Returns a Range object that represents the cell at the end of the region that
        contains the source range. Equivalent to pressing Ctrl+Up, Ctrl+down,
        Ctrl+left, or Ctrl+right.

        Parameters
        ----------
        direction : One of 'up', 'down', 'right', 'left'

        Examples
        --------
        >>> import xlwings as xw
        >>> wb = xw.Book()
        >>> sheet1 = xw.sheets[0]
        >>> sheet1.range('A1:B2').value = 1
        >>> sheet1.range('A1').end('down')
        <Range [Book1]Sheet1!$A$2>
        >>> sheet1.range('B2').end('right')
        <Range [Book1]Sheet1!$B$2>

        .. versionadded:: 0.9.0
        """
        return Range(impl=self.impl.end(direction))

    @property
    def formula(self):
        """Gets or sets the formula for the given Range."""
        return self.impl.formula

    @formula.setter
    def formula(self, value):
        self.impl.formula = value

    @property
    def formula2(self):
        """Gets or sets the formula2 for the given Range."""
        return self.impl.formula2

    @formula2.setter
    def formula2(self, value):
        self.impl.formula2 = value

    @property
    def formula_array(self):
        """
        Gets or sets an  array formula for the given Range.

        .. versionadded:: 0.7.1
        """
        return self.impl.formula_array

    @formula_array.setter
    def formula_array(self, value):
        self.impl.formula_array = value

    @property
    def font(self):
        return Font(impl=self.impl.font)

    @property
    def characters(self):
        return Characters(impl=self.impl.characters)

    @property
    def column_width(self):
        """
        Gets or sets the width, in characters, of a Range.
        One unit of column width is equal to the width of one character in the Normal
        style. For proportional fonts, the width of the character 0 (zero) is used.

        If all columns in the Range have the same width, returns the width.
        If columns in the Range have different widths, returns None.

        column_width must be in the range:
        0 <= column_width <= 255

        Note: If the Range is outside the used range of the Worksheet, and columns in
        the Range have different widths, returns the width of the first column.

        Returns
        -------
        float


        .. versionadded:: 0.4.0
        """
        return self.impl.column_width

    @column_width.setter
    def column_width(self, value):
        self.impl.column_width = value

    @property
    def row_height(self):
        """
        Gets or sets the height, in points, of a Range.
        If all rows in the Range have the same height, returns the height.
        If rows in the Range have different heights, returns None.

        row_height must be in the range:
        0 <= row_height <= 409.5

        Note: If the Range is outside the used range of the Worksheet, and rows in the
        Range have different heights, returns the height of the first row.

        Returns
        -------
        float


        .. versionadded:: 0.4.0
        """
        return self.impl.row_height

    @row_height.setter
    def row_height(self, value):
        self.impl.row_height = value

    @property
    def width(self):
        """
        Returns the width, in points, of a Range. Read-only.

        Returns
        -------
        float


        .. versionadded:: 0.4.0
        """
        return self.impl.width

    @property
    def height(self):
        """
        Returns the height, in points, of a Range. Read-only.

        Returns
        -------
        float


        .. versionadded:: 0.4.0
        """
        return self.impl.height

    @property
    def left(self):
        """
        Returns the distance, in points, from the left edge of column A to the left
        edge of the range. Read-only.

        Returns
        -------
        float


        .. versionadded:: 0.6.0
        """
        return self.impl.left

    @property
    def top(self):
        """
        Returns the distance, in points, from the top edge of row 1 to the top edge of
        the range. Read-only.

        Returns
        -------
        float


        .. versionadded:: 0.6.0
        """
        return self.impl.top

    @property
    def number_format(self):
        """
        Gets and sets the number_format of a Range.

        Examples
        --------
        >>> import xlwings as xw
        >>> wb = xw.Book()
        >>> sheet1 = wb.sheets[0]
        >>> sheet1.range('A1').number_format
        'General'
        >>> sheet1.range('A1:C3').number_format = '0.00%'
        >>> sheet1.range('A1:C3').number_format
        '0.00%'

        .. versionadded:: 0.2.3
        """
        return self.impl.number_format

    @number_format.setter
    def number_format(self, value):
        self.impl.number_format = value

    def get_address(
        self,
        row_absolute=True,
        column_absolute=True,
        include_sheetname=False,
        external=False,
    ):
        """
        Returns the address of the range in the specified format. ``address`` can be
        used instead if none of the defaults need to be changed.

        Arguments
        ---------
        row_absolute : bool, default True
            Set to True to return the row part of the reference as an absolute
            reference.

        column_absolute : bool, default True
            Set to True to return the column part of the reference as an absolute
            reference.

        include_sheetname : bool, default False
            Set to True to include the Sheet name in the address. Ignored if
            external=True.

        external : bool, default False
            Set to True to return an external reference with workbook and worksheet
            name.

        Returns
        -------
        str

        Examples
        --------
        ::

            >>> import xlwings as xw
            >>> wb = xw.Book()
            >>> sheet1 = wb.sheets[0]
            >>> sheet1.range((1,1)).get_address()
            '$A$1'
            >>> sheet1.range((1,1)).get_address(False, False)
            'A1'
            >>> sheet1.range((1,1), (3,3)).get_address(True, False, True)
            'Sheet1!A$1:C$3'
            >>> sheet1.range((1,1), (3,3)).get_address(True, False, external=True)
            '[Book1]Sheet1!A$1:C$3'

        .. versionadded:: 0.2.3
        """

        if include_sheetname and not external:
            # TODO: when the Workbook name contains spaces but not the Worksheet name,
            #  it will still be surrounded
            # by '' when include_sheetname=True. Also, should probably changed to regex
            temp_str = self.impl.get_address(row_absolute, column_absolute, True)

            if temp_str.find("[") > -1:
                results_address = temp_str[temp_str.rfind("]") + 1 :]
                if results_address.find("'") > -1:
                    results_address = "'" + results_address
                return results_address
            else:
                return temp_str

        else:
            return self.impl.get_address(row_absolute, column_absolute, external)

    @property
    def address(self):
        """
        Returns a string value that represents the range reference.
        Use ``get_address()`` to be able to provide paramaters.

        .. versionadded:: 0.9.0
        """
        return self.impl.address

    @property
    def current_region(self):
        """
        This property returns a Range object representing a range bounded by (but not
        including) any combination of blank rows and blank columns or the edges of the
        worksheet. It corresponds to ``Ctrl-*`` on Windows and ``Shift-Ctrl-Space`` on
        Mac.

        Returns
        -------
        Range object
        """

        return Range(impl=self.impl.current_region)

    def autofit(self):
        """
        Autofits the width and height of all cells in the range.

        * To autofit only the width of the columns use
          ``myrange.columns.autofit()``
        * To autofit only the height of the rows use
          ``myrange.rows.autofit()``

        .. versionchanged:: 0.9.0
        """
        return self.impl.autofit()

    @property
    def color(self):
        """
        Gets and sets the background color of the specified Range.

        To set the color, either use an RGB tuple ``(0, 0, 0)`` or a hex string
        like ``#efefef`` or an Excel color constant.
        To remove the background, set the color to ``None``, see Examples.

        Returns
        -------
        RGB : tuple

        Examples
        --------
        >>> import xlwings as xw
        >>> wb = xw.Book()
        >>> sheet1 = xw.sheets[0]
        >>> sheet1.range('A1').color = (255, 255, 255)  # or '#ffffff'
        >>> sheet1.range('A2').color
        (255, 255, 255)
        >>> sheet1.range('A2').color = None
        >>> sheet1.range('A2').color is None
        True

        .. versionadded:: 0.3.0
        """
        return self.impl.color

    @color.setter
    def color(self, color_or_rgb):
        self.impl.color = color_or_rgb

    @property
    def name(self):
        """
        Sets or gets the name of a Range.

        .. versionadded:: 0.4.0
        """
        impl = self.impl.name
        return impl and Name(impl=impl)

    @name.setter
    def name(self, value):
        self.impl.name = value

    def __call__(self, *args):
        return Range(impl=self.impl(*args))

    @property
    def rows(self):
        """
        Returns a :class:`RangeRows` object that represents the rows in the specified
        range.

        .. versionadded:: 0.9.0
        """
        return RangeRows(self)

    @property
    def columns(self):
        """
        Returns a :class:`RangeColumns` object that represents the columns in the
        specified range.

        .. versionadded:: 0.9.0
        """
        return RangeColumns(self)

    @property
    def shape(self):
        """
        Tuple of Range dimensions.

        .. versionadded:: 0.3.0
        """
        return self.impl.shape

    @property
    def size(self):
        """
        Number of elements in the Range.

        .. versionadded:: 0.3.0
        """
        a, b = self.shape
        return a * b

    @property
    def value(self):
        """
        Gets and sets the values for the given Range. See :meth:`xlwings.Range.options`
        about how to set options, e.g., to transform it into a DataFrame or how to set
        a chunksize.

        Returns
        -------
        object : returned object depends on the converter being used,
                 see :meth:`xlwings.Range.options`
        """
        return conversion.read(self, None, self._options)

    @value.setter
    def value(self, data):
        conversion.write(data, self, self._options)

    def expand(self, mode="table"):
        """
        Expands the range according to the mode provided. Ignores empty top-left cells
        (unlike ``Range.end()``).

        Parameters
        ----------
        mode : str, default 'table'
            One of ``'table'`` (=down and right), ``'down'``, ``'right'``.

        Returns
        -------
        Range

        Examples
        --------

        >>> import xlwings as xw
        >>> wb = xw.Book()
        >>> sheet1 = wb.sheets[0]
        >>> sheet1.range('A1').value = [[None, 1], [2, 3]]
        >>> sheet1.range('A1').expand().address
        $A$1:$B$2
        >>> sheet1.range('A1').expand('right').address
        $A$1:$B$1

        .. versionadded:: 0.9.0
        """
        return expansion.expanders.get(mode, mode).expand(self)

    def __getitem__(self, key):
        if type(key) is tuple:
            row, col = key

            n = self.shape[0]
            if isinstance(row, slice):
                row1, row2, step = row.indices(n)
                if step != 1:
                    raise ValueError("Slice steps not supported.")
                row2 -= 1
            elif isinstance(row, int):
                if row < 0:
                    row += n
                if row < 0 or row >= n:
                    raise IndexError("Row index %s out of range (%s rows)." % (row, n))
                row1 = row2 = row
            else:
                raise TypeError(
                    "Row indices must be integers or slices, not %s"
                    % type(row).__name__
                )

            n = self.shape[1]
            if isinstance(col, slice):
                col1, col2, step = col.indices(n)
                if step != 1:
                    raise ValueError("Slice steps not supported.")
                col2 -= 1
            elif isinstance(col, int):
                if col < 0:
                    col += n
                if col < 0 or col >= n:
                    raise IndexError(
                        "Column index %s out of range (%s columns)." % (col, n)
                    )
                col1 = col2 = col
            else:
                raise TypeError(
                    "Column indices must be integers or slices, not %s"
                    % type(col).__name__
                )

            return self.sheet.range(
                (
                    self.row + row1,
                    self.column + col1,
                    max(0, row2 - row1 + 1),
                    max(0, col2 - col1 + 1),
                )
            )

        elif isinstance(key, slice):
            if self.shape[0] > 1 and self.shape[1] > 1:
                raise IndexError(
                    "One-dimensional slicing is not allowed on two-dimensional ranges"
                )

            if self.shape[0] > 1:
                return self[key, :]
            else:
                return self[:, key]

        elif isinstance(key, int):
            n = len(self)
            k = key + n if key < 0 else key
            if k < 0 or k >= n:
                raise IndexError("Index %s out of range (%s elements)." % (key, n))
            else:
                return self(k + 1)

        else:
            raise TypeError(
                "Cell indices must be integers or slices, not %s" % type(key).__name__
            )

    def __repr__(self):
        return "<Range [{1}]{0}!{2}>".format(
            self.sheet.name, self.sheet.book.name, self.address
        )

    def insert(self, shift=None, copy_origin="format_from_left_or_above"):
        """
        Insert a cell or range of cells into the sheet.

        Parameters
        ----------
        shift : str, default None
            Use ``right`` or ``down``. If omitted, Excel decides based on the shape of
            the range.
        copy_origin : str, default format_from_left_or_above
            Use ``format_from_left_or_above`` or ``format_from_right_or_below``.
            Note that this is not supported on macOS.

        Returns
        -------
        None

        """
        self.impl.insert(shift, copy_origin)

    def delete(self, shift=None):
        """
        Deletes a cell or range of cells.

        Parameters
        ----------
        shift : str, default None
            Use ``left`` or ``up``. If omitted, Excel decides based on the shape of
            the range.

        Returns
        -------
        None

        """
        self.impl.delete(shift)

    def copy(self, destination=None):
        """
        Copy a range to a destination range or clipboard.

        Parameters
        ----------
        destination : xlwings.Range
            xlwings Range to which the specified range will be copied. If omitted,
            the range is copied to the clipboard.

        Returns
        -------
        None

        """
        self.impl.copy(destination)

    def paste(self, paste=None, operation=None, skip_blanks=False, transpose=False):
        """
        Pastes a range from the clipboard into the specified range.

        Parameters
        ----------
        paste : str, default None
            One of ``all_merging_conditional_formats``, ``all``, ``all_except_borders``,
            ``all_using_source_theme``, ``column_widths``, ``comments``, ``formats``,
            ``formulas``, ``formulas_and_number_formats``, ``validation``, ``values``,
            ``values_and_number_formats``.
        operation : str, default None
            One of "add", "divide", "multiply", "subtract".
        skip_blanks : bool, default False
            Set to ``True`` to skip over blank cells
        transpose : bool, default False
            Set to ``True`` to transpose rows and columns.

        Returns
        -------
        None

        """
        self.impl.paste(
            paste=paste,
            operation=operation,
            skip_blanks=skip_blanks,
            transpose=transpose,
        )

    @property
    def hyperlink(self):
        """
        Returns the hyperlink address of the specified Range (single Cell only)

        Examples
        --------
        >>> import xlwings as xw
        >>> wb = xw.Book()
        >>> sheet1 = wb.sheets[0]
        >>> sheet1.range('A1').value
        'www.xlwings.org'
        >>> sheet1.range('A1').hyperlink
        'http://www.xlwings.org'

        .. versionadded:: 0.3.0
        """
        if self.formula.lower().startswith("="):
            # If it's a formula, extract the URL from the formula string
            formula = self.formula
            try:
                return re.compile(r"\"(.+?)\"").search(formula).group(1)
            except AttributeError:
                raise Exception("The cell doesn't seem to contain a hyperlink!")
        else:
            # If it has been set pragmatically
            return self.impl.hyperlink

    def add_hyperlink(self, address, text_to_display=None, screen_tip=None):
        """
        Adds a hyperlink to the specified Range (single Cell)

        Arguments
        ---------
        address : str
            The address of the hyperlink.
        text_to_display : str, default None
            The text to be displayed for the hyperlink. Defaults to the hyperlink
            address.
        screen_tip: str, default None
            The screen tip to be displayed when the mouse pointer is paused over the
            hyperlink. Default is set to '<address> - Click once to follow. Click and
            hold to select this cell.'


        .. versionadded:: 0.3.0
        """
        if text_to_display is None:
            text_to_display = address
        if address[:4] == "www.":
            address = "http://" + address
        if screen_tip is None:
            screen_tip = (
                address + " - Click once to follow. Click and hold to select this cell."
            )
        self.impl.add_hyperlink(address, text_to_display, screen_tip)

    def resize(self, row_size=None, column_size=None):
        """
        Resizes the specified Range

        Arguments
        ---------
        row_size: int > 0
            The number of rows in the new range (if None, the number of rows in the
            range is unchanged).
        column_size: int > 0
            The number of columns in the new range (if None, the number of columns in
            the range is unchanged).

        Returns
        -------
        Range object: Range


        .. versionadded:: 0.3.0
        """

        if row_size is not None:
            assert row_size > 0
        else:
            row_size = self.shape[0]
        if column_size is not None:
            assert column_size > 0
        else:
            column_size = self.shape[1]

        return Range(self(1, 1), self(row_size, column_size)).options(**self._options)

    def offset(self, row_offset=0, column_offset=0):
        """
        Returns a Range object that represents a Range that's offset from the
        specified range.

        Returns
        -------
        Range object : Range


        .. versionadded:: 0.3.0
        """
        return Range(
            self(row_offset + 1, column_offset + 1),
            self(row_offset + self.shape[0], column_offset + self.shape[1]),
        ).options(**self._options)

    @property
    def last_cell(self):
        """
        Returns the bottom right cell of the specified range. Read-only.

        Returns
        -------
        Range

        Example
        -------
        >>> import xlwings as xw
        >>> wb = xw.Book()
        >>> sheet1 = wb.sheets[0]
        >>> myrange = sheet1.range('A1:E4')
        >>> myrange.last_cell.row, myrange.last_cell.column
        (4, 5)

        .. versionadded:: 0.3.5
        """
        return self(self.shape[0], self.shape[1]).options(**self._options)

    def select(self):
        """
        Selects the range. Select only works on the active book.

        .. versionadded:: 0.9.0
        """
        self.impl.select()

    @property
    def merge_area(self):
        """
        Returns a Range object that represents the merged Range containing the
        specified cell. If the specified cell isn't in a merged range, this property
        returns the specified cell.

        """
        return Range(impl=self.impl.merge_area)

    @property
    def merge_cells(self):
        """
        Returns ``True`` if the Range contains merged cells, otherwise ``False``
        """
        return self.impl.merge_cells

    def merge(self, across=False):
        """
        Creates a merged cell from the specified Range object.

        Parameters
        ----------
        across : bool, default False
            True to merge cells in each row of the specified Range as separate merged
            cells.
        """
        with self.sheet.book.app.properties(display_alerts=False):
            self.impl.merge(across)

    def unmerge(self):
        """
        Separates a merged area into individual cells.
        """
        self.impl.unmerge()

    @property
    def table(self):
        """
        Returns a Table object if the range is part of one, otherwise ``None``.

        .. versionadded:: 0.21.0
        """
        if self.impl.table:
            return Table(impl=self.impl.table)
        else:
            return None

    @property
    def wrap_text(self):
        """
        Returns ``True`` if the wrap_text property is enabled and ``False`` if it's
        disabled. If not all cells have the same value in a range, on Windows it returns
        ``None`` and on macOS ``False``.

        .. versionadded:: 0.23.2
        """
        return self.impl.wrap_text

    @wrap_text.setter
    def wrap_text(self, value):
        self.impl.wrap_text = value

    @property
    def note(self):
        """
        Returns a Note object.
        Before the introduction of threaded comments, a Note was called a Comment.

        .. versionadded:: 0.24.2
        """
        return Note(impl=self.impl.note) if self.impl.note else None

    def copy_picture(self, appearance="screen", format="picture"):
        """
        Copies the range to the clipboard as picture.

        Parameters
        ----------
        appearance : str, default 'screen'
            Either 'screen' or 'printer'.

        format : str, default 'picture'
            Either 'picture' or 'bitmap'.


        .. versionadded:: 0.24.8
        """
        self.impl.copy_picture(appearance, format)

    def to_png(self, path=None):
        """
        Exports the range as PNG picture.

        Parameters
        ----------

        path : str or path-like, default None
            Path where you want to store the picture. Defaults to the name of the range
            in the same directory as the Excel file if the Excel file is stored and to
            the current working directory otherwise.


        .. versionadded:: 0.24.8
        """
        if not PIL:
            raise XlwingsError("Range.to_png() requires an installation of Pillow.")
        path = utils.fspath(path)
        if path is None:
            # TODO: factor this out as it's used in multiple locations
            directory, _ = os.path.split(self.sheet.book.fullname)
            default_name = (
                str(self)
                .replace("<", "")
                .replace(">", "")
                .replace(":", "_")
                .replace(" ", "")
            )
            if directory:
                path = os.path.join(directory, default_name + ".png")
            else:
                path = str(Path.cwd() / default_name) + ".png"
        self.impl.to_png(path)

    def to_pdf(self, path=None, layout=None, show=None, quality="standard"):
        """
        Exports the range as PDF.

        Parameters
        ----------

        path : str or path-like, default None
            Path where you want to store the pdf. Defaults to the address of the range
            in the same directory as the Excel file if the Excel file is stored and to
            the current working directory otherwise.

        layout : str or path-like object, default None
            This argument requires xlwings :bdg-secondary:`PRO`.

            Path to a PDF file on which the report will be printed. This is ideal for
            headers and footers as well as borderless printing of graphics/artwork. The
            PDF file either needs to have only 1 page (every report page uses the same
            layout) or otherwise needs the same amount of pages as the report (each
            report page is printed on the respective page in the layout PDF).

        show : bool, default False
            Once created, open the PDF file with the default application.

        quality : str, default ``'standard'``
            Quality of the PDF file. Can either be ``'standard'`` or ``'minimum'``.


        .. versionadded:: 0.26.2
        """
        return utils.to_pdf(self, path=path, layout=layout, show=show, quality=quality)
