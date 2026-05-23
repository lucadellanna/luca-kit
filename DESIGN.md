# Repository-level design decisions

## README install vs uninstall command format

Install commands use the short marketplace name (`lucadellanna`):

```
/plugin install luca-kit@lucadellanna
```

Uninstall commands use the full marketplace path (`lucadellanna/luca-kit`):

```
/plugin uninstall luca-kit@lucadellanna/luca-kit
```

The difference is intentional and consistent across all four plugins (luca-kit, luca-ops-kit,
luca-dev-kit, luca-reflection-kit). The Claude Code CLI accepts a short marketplace name for
install (the marketplace slug) but requires the full `<owner>/<repo>` path for uninstall (so
it can locate the plugin in the registry unambiguously). The `/luca-kit` suffix is the
repository name, not a copy-paste artifact.
