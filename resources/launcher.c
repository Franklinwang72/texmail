/*
 * latex2clip launcher — tiny native binary that execs the Python daemon.
 * Compiled into the .app bundle as the CFBundleExecutable.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <libgen.h>
#include <mach-o/dyld.h>

int main(int argc, char *argv[]) {
    /* Find our own path */
    char exe[4096];
    uint32_t sz = sizeof(exe);
    if (_NSGetExecutablePath(exe, &sz) != 0) {
        fprintf(stderr, "latex2clip: cannot determine executable path\n");
        return 1;
    }

    /* Resolve symlinks */
    char *real = realpath(exe, NULL);
    if (!real) real = exe;

    /* Go up: MacOS/ -> Contents/ -> .app/ -> parent dir */
    char *dir = dirname(real);   /* .../MacOS          */
    dir = dirname(dir);          /* .../Contents        */
    dir = dirname(dir);          /* .../latex2clip.app  */
    dir = dirname(dir);          /* .../<parent>        */

    /* Read project path from embedded config next to binary */
    char cfg_path[4096];
    snprintf(cfg_path, sizeof(cfg_path), "%s/Contents/Resources/project_dir", real);
    /* Resolve: dir of binary's realpath up to Contents */
    char res_path[4096];
    char *real2 = realpath(exe, NULL);
    if (!real2) real2 = exe;
    char *d1 = dirname(real2);  /* MacOS */
    char *d2 = dirname(d1);    /* Contents */
    snprintf(res_path, sizeof(res_path), "%s/Resources/project_dir", d2);

    FILE *f = fopen(res_path, "r");
    char project_dir[4096] = {0};
    if (f) {
        if (fgets(project_dir, sizeof(project_dir), f)) {
            /* strip newline */
            project_dir[strcspn(project_dir, "\n")] = 0;
        }
        fclose(f);
    }

    if (project_dir[0] == '\0') {
        fprintf(stderr, "latex2clip: cannot read project_dir from Resources\n");
        return 1;
    }

    /* Build python path */
    char python[4096];
    snprintf(python, sizeof(python), "%s/.venv/bin/python", project_dir);

    /* Check venv exists */
    if (access(python, X_OK) != 0) {
        /* fallback to system python */
        strcpy(python, "/usr/local/bin/python3");
        if (access(python, X_OK) != 0) {
            strcpy(python, "/usr/bin/python3");
        }
    }

    /* Set PATH */
    setenv("PATH", "/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin", 1);

    /* Exec python — launch the windowed GUI */
    execl(python, "python3", "-c",
          "from latex2clip.gui import run_gui; run_gui()",
          NULL);

    perror("latex2clip: execl failed");
    return 1;
}
