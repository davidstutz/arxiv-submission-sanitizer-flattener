import os
import re
import sys
import argparse
import glob
import shutil


class SubmissionFlattener:
    """
    This is a simple script allowing to "flatten" an ArXiv submission.
    
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
    
    Here are some useful commands to resize or convert the images in case
    the generated PDF or ZIP file is still too large for ArXiv:
    * Resize images larger than 500px in width to 500px in width while not enlarging smaller ones:
        find . -name '*.jpg' -execdir convert {} -resize 500\> {} \;
    * Convert PNGs to JPGs with 95% quality:
        find . -name '*.png' -execdir mogrify -format jpg -quality 95 {} \;
    """

    def __init__(self):
        """
        Constructor.
        
        :param args: command line arguments
        """
        
        parser = self.get_parser()
        self.options = parser.parse_args()
        self.options.extensions = self.options.extensions.split(',')
        self.options.extensions = [extension.strip() for extension in self.options.extensions]
        
    def get_parser(self):
        """
        Get parser.
        
        :return: parser
        """
        
        parser = argparse.ArgumentParser(description='Submission flattener; run from root directory.')
        parser.add_argument('--mode', type=str, default='copy', help='Operation modes: `copy` copy files and update TEX files; `check`, same but with no actions.')
        parser.add_argument('--asset_directory', type=str, help='The (relative) path to the directory holding the assets.')
        parser.add_argument('--extensions', type=str, default='png', help='List of extensions to consider.')
        
        return parser
    
    def validate_options(self):
        """
        Validate options.
        """
        
        if self.options.mode != 'copy' and self.options.mode != 'check':
            print('The mode should be `copy` or `check`.')
            exit()
        if not os.path.exists(self.options.asset_directory):
            print('Asset directory %s not found.' % self.options.asset_directory)
            exit()
        if not os.path.isdir(self.options.asset_directory):
            print('Asset directory %s is not a directory.' % self.options.dep_directory)
            exit()
    
    def normalize_path(self, filepath):
        """
        Normalize a path.
        
        :param filepath: file path to normalize
        :return: normalized path
        """
        
        return os.path.normpath(os.path.relpath(filepath))
    
    def read_tex_files(self):
        """
        Read TeX files.
        
        :return: list of TEX files
        """
        
        files = []
        for filepath in glob.glob('*.tex'):
            files.append(self.normalize_path(filepath))
        
        return files
    
    def check_files(self, files):
        """
        Check the files referenced in DEP file.
        
        :param files: list of files from DEP file
        """
        
        for filepath in files:
            assert os.path.exists(filepath), 'File %s, found in DEP file, not found; did you check that your LaTeX file compiles?' % filepath
        
    def read_asset_directory(self):
        """
        Read files in asset directory.
        
        :return: files in asset directory
        """
        
        files = []
        for root, directories, filenames in os.walk(self.options.asset_directory):
            for filename in filenames:
                filepath = os.path.join(root, filename)
                filepath = self.normalize_path(filepath)
                _, extension = os.path.splitext(filepath)
                if extension[1:] in self.options.extensions:
                    files.append(filepath)
        
        return files
        
    def update_filepath(self, filepath, consider_extension=True):
        """
        Update a file path.
        
        :param filepath: path to file
        :param consider_extension: also consider the file's extension
        :return: updated file path
        """
        
        new_filepath = filepath.replace(os.sep, '_')
        if consider_extension:
            new_filepath, extension = os.path.splitext(new_filepath)
        new_filepath = new_filepath.replace('.', '_')
        if consider_extension:
            new_filepath = new_filepath + extension
        
        replace = {
            # Add abbreviations here:
            'long_filename_part': 'short_filename_part',
        }
        
        for key in replace.keys():
            new_filepath = new_filepath.replace(key, replace[key])
        
        assert len(new_filepath) < 64, 'new filepath %s not shorter than 64 characters' % new_filepath
        
        return new_filepath
        
    def run(self):
        """
        Run.
        """
        
        self.validate_options()
        asset_files = self.read_asset_directory()
        tex_files = self.read_tex_files()
        
        for asset_file in asset_files:
            new_asset_file = self.update_filepath(asset_file)
            if self.options.mode == 'copy':
                shutil.copyfile(asset_file, new_asset_file)
            print('Copied %s to %s' % (asset_file, new_asset_file))
        
        regexs = [
            # Add other include commands here:
            r"\\includegraphics\[[a-zA-Z0-9 =,\.\\\{\}]*\]\{(.*)\}",
            #'\\input\{(.*)\}',
        ]
        
        for regex in regexs:
            for t in range(len(tex_files)):
                tex_file = tex_files[t]
                print('Processing %s (%d/%d)' % (tex_file, t + 1, len(tex_files)))
                with open(tex_file, 'r') as f:
                    content = f.read()
                
                prog = re.compile(regex)
                matches = prog.findall(content)
                for match in matches:
                    new_match = self.update_filepath(match, True)
                    content = content.replace(match, new_match)
                    print('Replaced %s with %s' % (match, new_match))
                
                if self.options.mode == 'copy':
                    with open(tex_file, 'w') as f:
                        f.write(content)
                print('Updated %s' % tex_file)


if __name__ == '__main__':
    app = SubmissionFlattener()
    app.run()
    
