{ pkgs }: {
    deps = [
        pkgs.python310
        pkgs.python310Packages.pip
        pkgs.python310Packages.uvicorn
        pkgs.postgresql
        pkgs.redis
    ];
} 