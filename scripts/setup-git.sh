#!/bin/bash
git remote add juno-private git@github.com:alexi/juno-private.git
git branch --set-upstream-to=origin/main main
git branch --set-upstream-to=juno-private/private private