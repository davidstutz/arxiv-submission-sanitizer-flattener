# Submission Sanitizer & Flattener

This repository contains two simple scripts for cleaning up and flattening papers, for example for ArXiv.

## Cleaning Up

`sanitize_submission.py` is a simple Python script for cleaning up your submission files, especially image files or data files.
 
The problem addressed can be summarized easily: after performing experiments for a paper, it might not be clear
which results and visualizations actually make it into the paper. If you work like me, you might put a large part
of your results into a repository (or data storage) and change the actual figures in the paper frequently before the deadline.
As a result, your repository might hold a lot of data and image files which are not actually
used in the final paper.

Now, for uploading (or zipping) the paper to ArXiv, or making the LaTeX source available, you would like to delete
all unused data and image files without going through the LaTeX source manually. For this case,
there is `\RequirePackage{snapshot}` which, if added in the pre-amble, will create a `.deb` file
listing all used external resources.

Then, the script in this repository, `sanitize_submission.py` will go through this file and
delete all other files not needed.

**Use with caution and following the example below; code not thoroughly tested;
keep a backup of your files and LaTeX sources!**

**Example:** The image files of a paper ar in directory `images/`, then the `.dep` file obtained
after adding `\RequirePackage{snapshot}` in the pre-amble and compiling the paper 
-- let's call it `paper.dep` -- contains entries as follows:

    *{file}   {./images/experiments/kitti/vae_occ_aml/15_long/results_1.png}{0000/00/00 v0.0}
    *{file}   {./images/experiments/kitti/vae_occ_aml/15_long_statistics/results_1.png}{0000/00/00 v0.0}

These entries correspond to images used in the paper. Then,

    python sanitize_submission.py --mode=check --dep_file=paper.deb --asset_directory=images/ --extensions=png

Will look for `.png` files in `paper.deb` and in the given asset directory. It will
then list which files in the asset directory can be deleted as they do not appear in `paper.dep`.
After confirming that everything looks fine, run

    python sanitize_submission.py --mode=delete --dep_file=paper.deb --asset_directory=images/ --extensions=png

To perform deletion.

## Flattening

`flatten_submission.py` is a simple script allowing to "flatten" an ArXiv submission.
    
Given an asset directory and a set of extensions to look for, all files
are moved to the root directory, adding a prefix corresponding
to the original directory.

By default, the script just scans for \includegraphics statements, but this
can easily be changed in the `run` method.

Example: All images are stored in the `gfx/` directory in several
sub-directories. Use

    python flatten_submission.py --mode=check --asset_directory=gfx/ --extensions=png,jpg,jpeg

The `check` mode just scanes for all files and prints how they would be
moved/renamed. These changes can be made final using

    python flatten_submission.py --mode=copy --asset_directory=gfx/ --extensions=png,jpg,jpeg

## License

Copyright (c) 2018-2022 David Stutz

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
