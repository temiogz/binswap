#### Intro
`binswap` is a lightweight command-line utility script that monitors a directory for changes and auto relaunch an executable or script file whenever it's modified or replaced.

- Auto detects file creations, modifications, and deletions in the monitored directory.  
- Relaunches the executable or script whenever it's modified or replaced.  
- Handles termination of the old process before relaunching.  
- Supports script interpreters 

#### Usage
```sh
$ ./main.py --bin "executable_or_script_file" --dir "path/to/directory"
Ex: ./main.py --bin "script.js" --dir "path/to/directory"
```

```
Options
    -v, --version: Displays package version.
    -h, --help: Displays help message and usage information.
```