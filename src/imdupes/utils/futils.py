from sys import exit
import os
import re
from imagehash import ImageHash
from termcolor import cprint, colored

from utils.globs import SUPPORTED_FILE_EXTS
from utils.globs import INTERACTIVE_OPTS
from utils.globs import PathFormat, format_path


# noinspection DuplicatedCode
def index_images(
        directory: str,
        exclude: str = None,
        recursive: bool = False,
        verbose: bool = False
) -> list[str]:
    img_paths = []
    abs_root = os.path.abspath(directory)
    exclude_pattern = None if exclude is None else re.compile(exclude)

    if verbose:
        print('Indexing images...', end='', flush=True)

    if recursive:
        for root, dirs, files in os.walk(abs_root):
            for file in files:
                file_path = os.path.join(root, file)
                file_name = os.path.basename(file_path)
                if exclude_pattern is not None and exclude_pattern.search(file_name) is not None:
                    continue

                file_extension = os.path.splitext(file)[1].lower()[1:]
                if file_extension in SUPPORTED_FILE_EXTS:
                    img_paths.append(file_path)
    else:
        for file in os.listdir(abs_root):
            file_path = os.path.join(abs_root, file)
            if os.path.isfile(file_path):
                file_name = os.path.basename(file_path)
                if exclude_pattern is not None and exclude_pattern.search(file_name) is not None:
                    continue

                file_extension = os.path.splitext(file)[1].lower()[1:]
                if file_extension in SUPPORTED_FILE_EXTS:
                    img_paths.append(file_path)

    if len(img_paths) == 0:
        cprint(f' "{directory}" has no valid image files. Program terminated.', 'red')
        exit()

    if verbose:
        print(
            f' Found {colored(str(len(img_paths)), attrs=["bold"])} image(s) '
            f'{colored("[DONE]", color="green", attrs=["bold"])}',
            flush=True
        )

    return img_paths


def clean(
        dup_imgs: dict[ImageHash, list[str]],
        root_dir: str = None,
        interactive: bool = False,
        verbose: bool = False,
        output_path_format: PathFormat = PathFormat.DIR_RELATIVE
) -> None:
    if verbose:
        print(f'\nCleaning duplications...', flush=True)

    for dup_paths in dup_imgs.values():
        if interactive:
            for path in dup_paths:
                while True:
                    choices = '\n\t'.join(f'[{key.upper()}] {value}' for key, value in INTERACTIVE_OPTS.items())
                    choice = input(
                        f'Delete "{format_path(path, output_path_format, root_dir)}"?\n\t'
                        f'{colored(choices)}\n{colored(">>", "yellow", attrs=["bold"])} '
                    ).lower()

                    if choice in INTERACTIVE_OPTS.keys():
                        if choice == 'y':
                            try:
                                os.remove(path)
                                if verbose:
                                    print(f'-- Deleted "{format_path(path, output_path_format, root_dir)}"')
                            except OSError as e:
                                cprint(
                                    f'Error deleting file '
                                    f'"{format_path(path, output_path_format, root_dir)}": {str(e)}',
                                    'red'
                                )
                        if choice == 'x':
                            cprint('Cleaning cancelled. Program terminated.', 'red')
                            exit()

                        break

                    else:
                        print('Invalid choice. Please choose a valid option.')

        else:
            for i in range(1, len(dup_paths)):
                try:
                    os.remove(dup_paths[i])
                    if verbose:
                        print(f'-- Deleted "{format_path(dup_paths[i], output_path_format, root_dir)}"', flush=True)
                except OSError as e:
                    cprint(
                        f'Error deleting file "{format_path(dup_paths[i], output_path_format, root_dir)}": {str(e)}',
                        'red'
                    )

    if verbose:
        print(f'{colored("[DONE]", color="green", attrs=["bold"])}', flush=True)