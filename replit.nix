{ pkgs }: {
  deps = [
    pkgs.libsodium
    pkgs.cacert
    pkgs.python310Packages.opuslib
    pkgs.ffmpeg
    pkgs.replitPackages.prybar-python310
    pkgs.replitPackages.stderred
  ];
}