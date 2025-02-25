from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum
from typing import Any, ClassVar, TypeAlias

from kraken.common.toml import TomlFile

logger = logging.getLogger(__name__)


class _PackageIndexPriority(str, Enum):
    """
    Poetry has a very granular representation of priorities for indices, so we inherit that. The priority
    should to be interpreted in the spirit of its definition in other tools.

    https://python-poetry.org/docs/repositories/#project-configuration
    """

    default = "default"
    primary = "primary"
    secondary = "secondary"  # Do not use
    supplemental = "supplemental"


@dataclass
class PackageIndex:
    """
    Represents a Python package index. Some tool-specific representations of package indices may not support
    all fields, in which case the implementation should trigger a warning or error if the alternative behaviour
    conflicts with the field value.
    """

    Priority: ClassVar[TypeAlias] = _PackageIndexPriority

    #: A name for the package index.
    alias: str

    #: The URL to find the packages at.
    index_url: str

    #: The priority of the index. Not all tools support it exactly how we model it in here (e.g. like Poetry),
    #: so the corresponding #PyprojectHandler implementation may need to do some translation.
    priority: Priority

    #: Whether SSL should be verified when connecting to the index. Not all tools support this.
    verify_ssl: bool


class PyprojectHandler(ABC):
    """
    A wrapper for a raw TomlConfig to implement common read and mutation operations.
    """

    raw: TomlFile

    def __init__(self, raw: TomlFile) -> None:
        self.raw = raw

    def get_name(self) -> str | None:
        """
        Returns the current project name.

        This returns the name from the `project` section of the Pyproject.toml file as per PEP 621 [1].

        [1]: https://peps.python.org/pep-0621/#name
        """

        return self.raw.get("project", {}).get("name")  # type: ignore[no-any-return]

    def get_python_version_constraint(self) -> str | None:
        """
        Returns the current Python version constraint.

        This returns the Python version constraint from the `project` section of the Pyproject.toml file as per
        PEP 621 [1].

        [1]: https://peps.python.org/pep-0621/#requires-python
        """

        return self.raw.get("project", {}).get("requires-python")  # type: ignore[no-any-return]

    def get_version(self) -> str | None:
        """
        Returns the current project version. Returns #None if the project version can not be determined.

        This returns the version from the `project` section of the Pyproject.toml file as per PEP 621 [1].

        [1]: https://peps.python.org/pep-0621/#version
        """

        return self.raw.get("project", {}).get("version")  # type: ignore[no-any-return]

    def set_version(self, version: str | None) -> None:
        """
        Set (or unset) the project version.

        This sets the version from the `project` section of the Pyproject.toml file as per PEP 621 [1].

        [1]: https://peps.python.org/pep-0621/#version
        """

        project: dict[str, Any] | None = self.raw.get("project")
        if project is None:
            if version is None:
                return
            project = {"version": version}
            self.raw["project"] = project
        else:
            if version is None:
                project.pop("version", None)
            else:
                project["version"] = version

    def get_package_indexes(self) -> list[PackageIndex]:
        raise NotImplementedError("%s.get_package_indexes()" % type(self).__name__)

    def set_package_indexes(self, indexes: Sequence[PackageIndex]) -> None:
        raise NotImplementedError("%s.set_package_indexes()" % type(self).__name__)

    def set_path_dependencies_to_version(self, version: str) -> None:
        """
        Update all dependencies in the Pyproject that are path dependencies to the given version instead
        (such that they are no longer path dependencies).
        """

        raise NotImplementedError("%s.set_path_dependencies_to_version()" % type(self).__name__)

    @dataclass(frozen=True)
    class Package:
        include: str
        from_: str | None = None

    @abstractmethod
    def get_packages(self) -> list[Package]:
        pass


# Define Pyproject type for back compatibility
Pyproject = TomlFile
