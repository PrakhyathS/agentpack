from agentpack.ingest.tables import flatten_spurious_tables


def test_flattens_sparse_header_block():
    # Modeled on real markitdown PDF output: a run of mostly-blank-cell
    # "table" rows that are really just a document header, one field per line.
    text = (
        "|                       |     | CS648    | : Randomized |            |      | Algorithms |             |\n"
        "| --------------------- | --- | -------- | ------------ | ---------- | ---- | ---------- | ----------- |\n"
        "|                       |     | Semester | I, 2018-19,  |            | CSE, | IIT        | Kanpur      |\n"
        "|                       |     |          |              | Assignment |      | 1          |             |\n"
    )
    result = flatten_spurious_tables(text)

    assert "|" not in result
    assert "CS648" in result
    assert ": Randomized" in result
    assert "Semester" in result
    assert "Assignment" in result


def test_flattens_single_row_sentence_fragment():
    # A sentence split into a fake table with no data rows at all, no blank
    # cells — this is the case the empty-cell heuristic alone would miss.
    text = (
        "| • Each question | carries | 50 marks. | Total | marks | for this | assignment | are 150. |\n"
        "| --------------- | ------- | --------- | ----- | ----- | -------- | ---------- | -------- |\n"
    )
    result = flatten_spurious_tables(text)

    assert "|" not in result
    assert "Each question carries 50 marks." in result
    assert "Total marks for this assignment are 150." in result


def test_preserves_genuine_multi_row_table():
    text = (
        "| Name | Score | Grade |\n"
        "| --- | --- | --- |\n"
        "| Alice | 95 | A |\n"
        "| Bob | 82 | B |\n"
        "| Carol | 76 | C |\n"
    )
    result = flatten_spurious_tables(text)

    assert result.strip() == text.strip()


def test_leaves_plain_prose_untouched():
    text = "# Heading\n\nJust a normal paragraph with no tables at all.\n"
    assert flatten_spurious_tables(text) == text.rstrip("\n")


def test_handles_empty_input():
    assert flatten_spurious_tables("") == ""


def test_flattens_two_row_table_with_no_blank_cells():
    # Small tables (header + 1 data row) are treated as likely-spurious even
    # with zero blank cells — real intentional tables almost always have 2+
    # data rows.
    text = (
        "| Deadline | Time |\n"
        "| --- | --- |\n"
        "| Monday | 5pm |\n"
    )
    result = flatten_spurious_tables(text)

    assert "|" not in result
    assert "Deadline Time Monday 5pm" in result


def test_mixed_content_only_flattens_spurious_parts():
    text = (
        "# Assignment\n\n"
        "|                       |     | CS648    | : Randomized |            |      | Algorithms |             |\n"
        "| --------------------- | --- | -------- | ------------ | ---------- | ---- | ---------- | ----------- |\n"
        "|                       |     | Semester | I, 2018-19,  |            | CSE, | IIT        | Kanpur      |\n"
        "\n"
        "Some real prose here.\n"
        "\n"
        "| Name | Score | Grade |\n"
        "| --- | --- | --- |\n"
        "| Alice | 95 | A |\n"
        "| Bob | 82 | B |\n"
        "| Carol | 76 | C |\n"
    )
    result = flatten_spurious_tables(text)

    assert "CS648" in result and "| CS648" not in result
    assert "Some real prose here." in result
    assert "| Alice | 95 | A |" in result  # genuine table preserved verbatim
