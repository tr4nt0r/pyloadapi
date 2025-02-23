# Contributing

Contributions are welcome, and they are greatly appreciated! Every little bit helps, and credit will always be given.

You can contribute in many ways:

## Types of Contributions

### Report Bugs

Report bugs at <https://github.com/tr4nt0r/pyloadapi/issues>.

If you are reporting a bug, please include:

- Your operating system name and version.
- Any details about your local setup that might be helpful in troubleshooting.
- Detailed steps to reproduce the bug.

### Fix Bugs

Look through the GitHub issues for bugs. Anything tagged with "👻 bug" and "🙏🏼 help wanted" is open to whoever wants to implement it.

### Implement Features

Look through the GitHub issues for features. Anything tagged with "🚀 feature" and "🙏🏼 help wanted" is open to whoever wants to implement it.

### Write Documentation

PyLoadAPI could always use more documentation, whether as part of the official PyLoadAPI docs, in docstrings, or even on the web in blog posts, articles, and such.

### Submit Feedback

The best way to send feedback is to file an issue at <https://github.com/tr4nt0r/pyloadapi/issues>.

If you are proposing a feature:

- Explain in detail how it would work.
- Keep the scope as narrow as possible, to make it easier to implement.
- Remember that this is a volunteer-driven project, and that contributions are welcome :)

## Get Started!

Ready to contribute? Here's how to set up `PyLoadAPI` for local development.

1. Fork the `PyLoadAPI` repo on GitHub.

2. Clone your fork locally:

    ```shell
    $ git clone git@github.com:tr4nt0r/pyloadapi.git
    ```

3. Install your local copy using Hatch. Assuming you have Hatch installed, this is how you set up your fork for local development:

    ```shell
    $ cd pyloadapi
    $ hatch env create
    $ hatch shell
    ```

4. Create a branch for local development:

    ```shell
    $ git checkout -b name-of-your-bugfix-or-feature
    ```

    Now you can make your changes locally.

5.  When you're done making changes, check that your changes pass the tests and linting:

    ```shell
    $ hatch run lint
    $ hatch run test
    ```

6. Commit your changes and push your branch to GitHub:

    ``` shell
    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature
    ```

7. Submit a pull request through the GitHub website.

## Pull Request Guidelines

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put your new functionality into a function with a docstring, and add the feature to the list in README.md.
3. The pull request should work for Python 3.10 to 3.13. Check the [build workflow](https://github.com/tr4nt0r/pyloadapi/actions/workflows/build.yml) and make sure that the tests pass for all supported Python versions.

## Tips

To run tests across all supported Python versions:

```shell
$ hatch run test --all
```

To run a subset of tests:

```shell
$ hatch run test -- tests/test_api.py::test_login
```

## Deploying

For maintainers, here's a reminder on how to deploy. Ensure all changes are committed, including an entry in `CHANGELOG.md`. Then execute:

```shell
$ hatch version patch # options: major / minor / patch
$ git push
$ git push --tags
```

GitHub Actions will handle the deployment to PyPI if the tests pass. A release draft is created by a workflow that tracks all changes and determines the next version (patch, minor, or major) based on the labels assigned to the merged PRs. Review the draft to confirm the version bump.
