from kraken.std.git.gitignore.generated import join_generated_section, split_generated_section
from kraken.std.git.gitignore.parser import GitignoreFile

LEGACY_GITIGNORE = """
### START-GENERATED-CONTENT [HASH: 3d9a3142ccc0b9baed88a8427ff555e32ebc44d88e851c24d35a8e6ea7901ad3]
# -------------------------------------------------------------------------------------------------
# THIS SECTION WAS AUTOMATICALLY GENERATED BY KRAKEN; DO NOT MODIFY OR YOUR CHANGES WILL BE LOST.
# If you need to define custom gitignore rules, add them below
# -------------------------------------------------------------------------------------------------
### [PARAMETERS_HASH: 5a7dde844945ce553190de65b75086d9f6f05eec8cabc8c52cd0b202285a91a1]

# abc
foobar
# -------------------------------------------------------------------------------------------------
### END-GENERATED-CONTENT

custom
"""

NEW_GITIGNORE = """
# GENERATED-CONTENT-START
# Do not edit
foo
bar
# GENERATED-CONTENT-END
"""


def test__split_generated_section__can_parse_legacy_gitignore() -> None:
    user1, generated, user2 = split_generated_section(GitignoreFile.parse(LEGACY_GITIGNORE))
    assert user1 == [""]
    assert generated == [
        "",
        "# abc",
        "foobar",
    ]
    assert user2 == [
        "",
        "custom",
    ]


def test__split_generated_section__can_parse_new_gitignore() -> None:
    user1, generated, user2 = split_generated_section(GitignoreFile.parse(NEW_GITIGNORE))
    assert user1 == [""]
    assert generated == [
        "# Do not edit",
        "foo",
        "bar",
    ]
    assert user2 == []


def test__join_generated_section__same_as_parsed() -> None:
    user1, generated, user2 = split_generated_section(GitignoreFile.parse(NEW_GITIGNORE))
    assert NEW_GITIGNORE == "\n".join(join_generated_section(user1, generated, user2)) + "\n"