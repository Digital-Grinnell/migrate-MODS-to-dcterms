# migrate-MODS-to-dcterms

This project, built from [migrate-MODS-xml](https://github.com/Digital-Grinnell/migrate-MODS-xml) (which was built from [Map-MODS-to-MASTER](https://github.com/DigitalGrinnell/Map-MODS-to-MASTER)) codebase is intended to read a series of exported `.xml` files (see [Creating a Migration Collection](https://static.grinnell.edu/dlad-blog/posts/129-creating-a-migration-collection/) for an example) and translate them into an [Alma/dcterms](https://www.dublincore.org/specifications/dublin-core/dcmi-terms/)-compliant `.csv` file suitable for supporting object migration to Alma Digital.  

The code here borrows heavily from the aforementioned project's `main.py` script, and the `process_collection` function in particular.  This codebase was created using _VSCode_ following guidance provided in [Proper Python](https://blog.summittdweller.com/posts/2022/09/proper-python/).  

When entering this project environment in _VSCode_ you should always do this first:  

```sh
╭─mcfatem@MAC02FK0XXQ05Q ~/GitHub/migrate-MODS-to-dcterms ‹main› 
╰─$ source .venv/bin/activate
(.venv) ╭─mcfatem@MAC02FK0XXQ05Q ~/GitHub/migrate-MODS-to-dcterms ‹main› 
╰─$ 
```
 Then to run the script, for example in the `migration-test` collection directory:

 ```sh
 (.venv) ╭─mcfatem@MAC02FK0XXQ05Q ~/GitHub/migrate-MODS-to-dcterms ‹main› 
╰─$ cd migration-test 
(.venv) ╭─mcfatem@MAC02FK0XXQ05Q ~/GitHub/migrate-MODS-to-dcterms/migration-test ‹main› 
╰─$ python3 ../main.py
 ```
