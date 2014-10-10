Example Lecture Slides
======================

The files in this directory are used to create the [animation](http://www.briancjenkins.com/pdf/Slides_012_Bank_Assets_Liabilities.pdf) hosted on my personal website. The directory contains:

  1. **012_Bank_Assets_Liabilities.py**	Main Python script that retreives the appropriate data from FRED, edits the tables and produces figures for the slides, runs LaTeX, and cleans up the auxillary files created during typesetting.
  2. **fredclass.py**: The fredclass module
  3. **Slides_012_Bank_Assets_Liabilities.pdf** Sample slides.
  4. **Slides_012_Bank_Assets_Liabilities.tex**	Main LaTeX file for lecture slides.
  5. Figures created by 012_Bank_Assets_Liabilities.py:
    * **fig_012_bank_assets.png**
    * **fig_012_bank_liabilities.png**
  6. tex files for figures:
    * **fig_slides_012_bank_system_assets.tex**
    * **fig_slides_012_bank_system_liabilities.tex**
  7. tex files for tables:
    * **table_slides_012_bank_system_assets.tex**
    * **table_slides_012_bank_system_balance_sheet.tex**
    * **table_slides_012_bank_system_liabilities.tex**
    * **table_slides_012_bank_system_loans.tex**
    
  To create the lecture slides from scratch, download all files into the same directory. check the fredclass documentation to make sure that you have all of the required Python modules installed (numpy, statsmodels, etc). Run 012_Bank_Assets_Liabilities.py.
