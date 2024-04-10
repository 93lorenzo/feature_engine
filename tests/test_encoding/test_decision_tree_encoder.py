import numpy as np
import pandas as pd
import pytest

from feature_engine.encoding import DecisionTreeEncoder


def test_encoding_method_param(df_enc):
    # defaults
    encoder = DecisionTreeEncoder(regression=False)
    encoder.fit(df_enc, df_enc["target"])
    assert encoder.encoder_[0].encoding_method == "arbitrary"

    # ordered encoding
    encoder = DecisionTreeEncoder(encoding_method="ordered", regression=False)
    encoder.fit(df_enc[["var_A", "var_B"]], df_enc["target"])
    assert encoder.encoder_[0].encoding_method == "ordered"

    # incorrect input
    with pytest.raises(ValueError):
        encoder = DecisionTreeEncoder(encoding_method="other", regression=False)
        encoder.fit(df_enc, df_enc["target"])


def test_classification(df_enc):
    encoder = DecisionTreeEncoder(regression=False)
    encoder.fit(df_enc[["var_A", "var_B"]], df_enc["target"])
    X = encoder.transform(df_enc[["var_A", "var_B"]])

    transf_df = df_enc.copy()
    transf_df["var_A"] = [0.25] * 16 + [0.5] * 4  # Tree: var_A <= 1.5 -> 0.25 else 0.5
    transf_df["var_B"] = [0.2] * 10 + [0.4] * 10  # Tree: var_B <= 0.5 -> 0.2 else 0.4
    pd.testing.assert_frame_equal(X, transf_df[["var_A", "var_B"]])


def test_regression(df_enc):
    random = np.random.RandomState(42)
    y = random.normal(0, 0.1, len(df_enc))
    encoder = DecisionTreeEncoder(
        regression=True,
        random_state=random,
    )
    encoder.fit(df_enc[["var_A", "var_B"]], y)
    X = encoder.transform(df_enc[["var_A", "var_B"]])

    transf_df = df_enc.copy()
    transf_df["var_A"] = (
        [0.034348] * 6 + [-0.024679] * 10 + [-0.075473] * 4
    )  # Tree: var_A <= 1.5 -> 0.25 else 0.5
    transf_df["var_B"] = [0.044806] * 10 + [-0.079066] * 10
    pd.testing.assert_frame_equal(X.round(6), transf_df[["var_A", "var_B"]])


def test_fit_raises_error_if_df_contains_na(df_enc_na):
    # test case 4: when dataset contains na, fit method
    encoder = DecisionTreeEncoder(regression=False)
    with pytest.raises(ValueError) as record:
        encoder.fit(df_enc_na[["var_A", "var_B"]], df_enc_na["target"])
    msg = (
        "Some of the variables in the dataset contain NaN. Check and "
        "remove those before using this transformer."
    )
    assert str(record.value) == msg


def test_transform_raises_error_if_df_contains_na(df_enc, df_enc_na):
    # test case 4: when dataset contains na, transform method
    encoder = DecisionTreeEncoder(regression=False)
    encoder.fit(df_enc[["var_A", "var_B"]], df_enc["target"])
    with pytest.raises(ValueError) as record:
        encoder.transform(df_enc_na[["var_A", "var_B"]])
    msg = (
        "Some of the variables in the dataset contain NaN. Check and "
        "remove those before using this transformer."
    )
    assert str(record.value) == msg


def test_classification_ignore_format(df_enc_numeric):
    encoder = DecisionTreeEncoder(
        regression=False,
        ignore_format=True,
    )
    encoder.fit(df_enc_numeric[["var_A", "var_B"]], df_enc_numeric["target"])
    X = encoder.transform(df_enc_numeric[["var_A", "var_B"]])

    transf_df = df_enc_numeric.copy()
    transf_df["var_A"] = [0.25] * 16 + [0.5] * 4  # Tree: var_A <= 1.5 -> 0.25 else 0.5
    transf_df["var_B"] = [0.2] * 10 + [0.4] * 10  # Tree: var_B <= 0.5 -> 0.2 else 0.4
    pd.testing.assert_frame_equal(X, transf_df[["var_A", "var_B"]])


def test_regression_ignore_format(df_enc_numeric):
    random = np.random.RandomState(42)
    y = random.normal(0, 0.1, len(df_enc_numeric))
    encoder = DecisionTreeEncoder(
        regression=True,
        random_state=random,
        ignore_format=True,
    )
    encoder.fit(df_enc_numeric[["var_A", "var_B"]], y)
    X = encoder.transform(df_enc_numeric[["var_A", "var_B"]])

    transf_df = df_enc_numeric.copy()
    transf_df["var_A"] = (
        [0.034348] * 6 + [-0.024679] * 10 + [-0.075473] * 4
    )  # Tree: var_A <= 1.5 -> 0.25 else 0.5
    transf_df["var_B"] = [0.044806] * 10 + [-0.079066] * 10
    pd.testing.assert_frame_equal(X.round(6), transf_df[["var_A", "var_B"]])


def test_variables_cast_as_category(df_enc_category_dtypes):
    df = df_enc_category_dtypes.copy()
    encoder = DecisionTreeEncoder(regression=False)
    encoder.fit(df[["var_A", "var_B"]], df["target"])
    X = encoder.transform(df[["var_A", "var_B"]])

    transf_df = df.copy()
    transf_df["var_A"] = [0.25] * 16 + [0.5] * 4  # Tree: var_A <= 1.5 -> 0.25 else 0.5
    transf_df["var_B"] = [0.2] * 10 + [0.4] * 10  # Tree: var_B <= 0.5 -> 0.2 else 0.4
    pd.testing.assert_frame_equal(X, transf_df[["var_A", "var_B"]], check_dtype=False)
    assert X["var_A"].dtypes == float


def test_error_when_regression_is_true_and_target_is_binary(df_enc):
    encoder = DecisionTreeEncoder(regression=True)
    with pytest.raises(ValueError) as record:
        encoder.fit(df_enc[["var_A", "var_B"]], df_enc["target"])
    msg = (
        "Trying to fit a regression to a binary target is not "
        "allowed by this transformer. Check the target values "
        "or set regression to False."
    )
    assert str(record.value) == msg


def test_error_when_regression_is_false_and_target_is_continuous(df_enc):
    random = np.random.RandomState(42)
    y = random.normal(0, 10, len(df_enc))
    encoder = DecisionTreeEncoder(regression=False)
    # the error message comes from sklearn api - won't test
    with pytest.raises(ValueError):
        encoder.fit(df_enc[["var_A", "var_B"]], y)


def test_inverse_transform_raises_not_implemented_error(df_enc):
    random = np.random.RandomState(42)
    y = random.normal(0, 10, len(df_enc))
    encoder = DecisionTreeEncoder(regression=True).fit(df_enc[["var_A", "var_B"]], y)
    with pytest.raises(NotImplementedError) as record:
        encoder.inverse_transform(df_enc[["var_A", "var_B"]])
    msg = "inverse_transform is not implemented for this transformer."
    assert str(record.value) == msg


@pytest.mark.parametrize(
    "grid",
    [None, {"max_depth": [1, 2, 3]}, {"max_depth": [1, 2], "estimators": [10, 12]}],
)
def test_assigns_param_grid(grid):
    encoder = DecisionTreeEncoder(param_grid=grid)
    if grid is None:
        assert encoder._assign_param_grid() == {"max_depth": [1, 2, 3, 4]}
    else:
        assert encoder._assign_param_grid() == grid


def test_unseen_param(df_enc):
    # defaults
    encoder = DecisionTreeEncoder(regression=False)
    encoder.fit(df_enc, df_enc["target"])
    assert encoder.encoder_[0].unseen == "raise"

    # ignore unseen
    encoder = DecisionTreeEncoder(unseen="ignore", regression=False)
    encoder.fit(df_enc[["var_A", "var_B"]], df_enc["target"])
    assert encoder.encoder_[0].unseen == "ignore"

    # encode unseen
    encoder = DecisionTreeEncoder(unseen="encode", regression=False, fill_value=-1)
    encoder.fit(df_enc[["var_A", "var_B"]], df_enc["target"])
    assert encoder.encoder_[0].unseen == "encode"

    # incorrect input
    with pytest.raises(ValueError):
        encoder = DecisionTreeEncoder(regression=False,  unseen='wrong_text')
        encoder.fit(df_enc, df_enc["target"])


def test_fill_value_error(df_enc):
    # fill_value not defined
    with pytest.raises(ValueError):
        encoder = DecisionTreeEncoder(unseen="encode", regression=False)
        encoder.fit(df_enc[["var_A", "var_B"]], df_enc["target"])

    # np.nan
    with pytest.raises(ValueError):
        encoder = DecisionTreeEncoder(unseen="encode", regression=False,
                                      fill_value=np.nan)
        encoder.fit(df_enc[["var_A", "var_B"]], df_enc["target"])

    # None
    with pytest.raises(ValueError):
        encoder = DecisionTreeEncoder(unseen="encode", regression=False,
                                      fill_value=None)
        encoder.fit(df_enc[["var_A", "var_B"]], df_enc["target"])


def test_fit_no_errors_if_new_cat_values_and_unseen_is_encode_param(df_enc):

    encoder = DecisionTreeEncoder(
        unseen="encode",
        regression=False,
        fill_value=-1
    )

    encoder.fit(df_enc[["var_A", "var_B"]], df_enc["target"])
    X_unseen_values_1 = pd.DataFrame({
        "var_A": ['ZZZ', 'YYY'],
        "var_B": ['YYY', 'ZZZ'],
    })
    X_unseen_values_2 = pd.DataFrame({
        "var_A": ['XXX', -1],
        "var_B": ['WWW', -1],
    })

    transf_unseen_1 = encoder.transform(X_unseen_values_1)
    transf_unseen_2 = encoder.transform(X_unseen_values_2)
    # unseen categories must be encoded in the same way
    pd.testing.assert_frame_equal(transf_unseen_1, transf_unseen_2)


def test_fit_errors_if_new_cat_values_and_unseen_is_raise_param(df_enc):
    encoder = DecisionTreeEncoder(
        unseen='raise',
        regression=False
    )
    encoder.fit(df_enc[["var_A", "var_B"]], df_enc["target"])
    X_unseen_values = pd.DataFrame({
        "var_A": ['ZZZ', 'YYY'],
        "var_B": ['YYY', 'ZZZ'],
    })
    # new categories will raise an error
    with pytest.raises(ValueError):
        encoder.transform(X_unseen_values)


def test_unseen_for_regression_and_numeric_categories(df_enc_numeric):
    random = np.random.RandomState(42)
    y = random.normal(0, 0.1, len(df_enc_numeric))

    # pick a value we have in the dataset
    fill_value = df_enc_numeric["var_A"].tolist()[0]
    # pick unseen value
    unseen_value = -100

    encoder = DecisionTreeEncoder(
        regression=True,
        random_state=random,
        unseen="encode",
        fill_value=fill_value,
        ignore_format=True,
        variables=["var_A", "var_B"]
    )
    encoder.fit(df_enc_numeric[["var_A", "var_B"]], y)

    num_encode = pd.concat([
        df_enc_numeric[["var_A", "var_B"]],
        pd.DataFrame({
            "var_A": [unseen_value],
            "var_B": [unseen_value]
        })
    ])

    X = encoder.transform(num_encode)

    row_index_fill_value = num_encode.index[num_encode['var_A'] == fill_value][0]
    row_index_unseen_value = num_encode.index[num_encode['var_A'] == unseen_value][0]
    assert (X.iloc[row_index_fill_value]).equals(X.iloc[row_index_unseen_value])



def test_fit_no_errors_if_new_cat_values_and_unseen_is_encode_param(df_enc):

    encoder = DecisionTreeEncoder(
        unseen="encode",
        regression=False,
        fill_value=-1
    )

    encoder.fit(df_enc[["var_A", "var_B"]], df_enc["target"])
    X_unseen_values_1 = pd.DataFrame({
        "var_A": ['ZZZ', 'YYY'],
        "var_B": ['YYY', 'ZZZ'],
    })
    X_unseen_values_2 = pd.DataFrame({
        "var_A": ['XXX', -1],
        "var_B": ['WWW', -1],
    })

    transf_unseen_1 = encoder.transform(X_unseen_values_1)
    transf_unseen_2 = encoder.transform(X_unseen_values_2)
    # unseen categories must be encoded in the same way
    pd.testing.assert_frame_equal(transf_unseen_1, transf_unseen_2)


def test_fit_errors_if_new_cat_values_and_unseen_is_raise_param(df_enc):
    encoder = DecisionTreeEncoder(
        unseen='raise',
        regression=False
    )
    encoder.fit(df_enc[["var_A", "var_B"]], df_enc["target"])
    X_unseen_values = pd.DataFrame({
        "var_A": ['ZZZ', 'YYY'],
        "var_B": ['YYY', 'ZZZ'],
    })
    # new categories will raise an error
    with pytest.raises(ValueError):
        encoder.transform(X_unseen_values)
