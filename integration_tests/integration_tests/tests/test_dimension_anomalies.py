from datetime import date, timedelta
from typing import Any, Dict, List

from data_generator import DATE_FORMAT, generate_dates
from dbt_project import DbtProject

TIMESTAMP_COLUMN = "updated_at"
DIMENSION = "superhero"
DBT_TEST_NAME = "elementary.dimension_anomalies"
DBT_TEST_ARGS = {"timestamp_column": TIMESTAMP_COLUMN, "dimensions": [DIMENSION]}


def test_anomalyless_dimension_anomalies(test_id: str, dbt_project: DbtProject):
    dates = generate_dates(base_date=date.today() - timedelta(1))
    data: List[Dict[str, Any]] = sum(
        [
            [
                {
                    TIMESTAMP_COLUMN: cur_date.strftime(DATE_FORMAT),
                    DIMENSION: "Superman",
                },
                {
                    TIMESTAMP_COLUMN: cur_date.strftime(DATE_FORMAT),
                    DIMENSION: "Batman",
                },
            ]
            for cur_date in dates
        ],
        [],
    )
    test_result = dbt_project.test(data, test_id, DBT_TEST_NAME, DBT_TEST_ARGS)
    assert test_result["status"] == "pass"


def test_anomalous_dimension_anomalies(test_id: str, dbt_project: DbtProject):
    dates = generate_dates(base_date=date.today() - timedelta(1))
    data: List[Dict[str, Any]] = [
        {
            TIMESTAMP_COLUMN: dates[0],
            DIMENSION: "Superman",
        },
        {
            TIMESTAMP_COLUMN: dates[0],
            DIMENSION: "Superman",
        },
        {
            TIMESTAMP_COLUMN: dates[0],
            DIMENSION: "Superman",
        },
        {
            TIMESTAMP_COLUMN: dates[0],
            DIMENSION: "Batman",
        },
    ] + sum(
        [
            [
                {
                    TIMESTAMP_COLUMN: cur_date.strftime(DATE_FORMAT),
                    DIMENSION: "Superman",
                },
                {
                    TIMESTAMP_COLUMN: cur_date.strftime(DATE_FORMAT),
                    DIMENSION: "Batman",
                },
            ]
            for cur_date in dates[1:]
        ],
        [],
    )
    test_result = dbt_project.test(data, test_id, DBT_TEST_NAME, DBT_TEST_ARGS)
    assert test_result["status"] == "fail"


def test_dimensions_anomalies_with_where_parameter(
    test_id: str, dbt_project: DbtProject
):
    dates = generate_dates(base_date=date.today() - timedelta(1))
    data: List[Dict[str, Any]] = [
        {
            TIMESTAMP_COLUMN: dates[0],
            "universe": "DC",
            DIMENSION: "Superman",
        },
        {
            TIMESTAMP_COLUMN: dates[0],
            "universe": "DC",
            DIMENSION: "Superman",
        },
        {
            TIMESTAMP_COLUMN: dates[0],
            "universe": "DC",
            DIMENSION: "Superman",
        },
        {
            TIMESTAMP_COLUMN: dates[0],
            "universe": "Marvel",
            DIMENSION: "Spiderman",
        },
    ] + sum(
        [
            [
                {
                    TIMESTAMP_COLUMN: cur_date.strftime(DATE_FORMAT),
                    "universe": "DC",
                    DIMENSION: "Superman",
                },
                {
                    TIMESTAMP_COLUMN: cur_date.strftime(DATE_FORMAT),
                    "universe": "Marvel",
                    DIMENSION: "Spiderman",
                },
            ]
            for cur_date in dates[1:]
        ],
        [],
    )

    params_without_where = DBT_TEST_ARGS
    result_without_where = dbt_project.test(
        data, test_id, DBT_TEST_NAME, params_without_where
    )
    assert result_without_where["status"] == "fail"

    params_with_where = dict(params_without_where, where="universe = 'Marvel'")
    result_with_where = dbt_project.test(
        data, test_id, DBT_TEST_NAME, params_with_where
    )
    assert result_with_where["status"] == "pass"

    params_with_where2 = dict(params_without_where, where="universe = 'DC'")
    result_with_where2 = dbt_project.test(
        data, test_id, DBT_TEST_NAME, params_with_where2
    )
    assert result_with_where2["status"] == "fail"
