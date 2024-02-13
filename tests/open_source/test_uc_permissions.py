from mlflow_export_import.common.uc_permissions_utils import _mk_update_changes, _mk_unrolled_changes


# == Standard upate

ref_input_perms = {
  "permissions": {
    "privilege_assignments": [
      {
        "principal": "denali@mycompany.com",
        "privileges": [
          "ALL_PRIVILEGES",
          "EXECUTE"
        ]
      },
      {
        "principal": "aconcagua@mycompany.com",
        "privileges": [
          "EXECUTE"
        ]
      }
    ]
  },
  "effective_permissions": {
    "privilege_assignments": [
      {
        "principal": "denali@mycompany.com",
        "privileges": [
          {
            "privilege": "ALL_PRIVILEGES"
          },
          {
            "privilege": "EXECUTE"
          },
          {
            "privilege": "EXECUTE",
            "inherited_from_type": "SCHEMA",
            "inherited_from_name": "my_catalog.my_models"
          }
        ]
      },
      {
        "principal": "aconcagua@mycompany.com",
        "privileges": [
          {
            "privilege": "EXECUTE"
          }
        ]
      },
      {
        "principal": "account users",
        "privileges": [
          {
            "privilege": "ALL_PRIVILEGES",
            "inherited_from_type": "CATALOG",
            "inherited_from_name": "my_catalog"
          }
        ]
      }
    ]
  }
}

ref_changes = {
  "changes": [
    {
      "principal": "denali@mycompany.com",
      "add": [
        "ALL_PRIVILEGES",
        "EXECUTE",
        "EXECUTE"
      ]
    },
    {
      "principal": "aconcagua@mycompany.com",
      "add": [
        "EXECUTE"
      ]
    },
    {
      "principal": "account users",
      "add": [
        "ALL_PRIVILEGES"
      ]
    }
  ]
}


def test_uc_permission_mapping():
    changes = _mk_update_changes(ref_input_perms)
    assert changes == ref_changes


# == Unrolled update

ref_changes_2 = {
  "changes": [
    {
      "principal": "denali@mycompany.com",
      "add": [
        "ALL_PRIVILEGES",
        "EXECUTE"
      ]
    },
    {
      "principal": "aconcagua@mycompany.com",
      "add": [
        "EXECUTE"
      ]
    }
  ]
}

ref_unrolled_changes = [
  {
    "changes": [
      {
        "principal": "denali@mycompany.com",
        "add": [
          "ALL_PRIVILEGES",
          "EXECUTE"
        ]
      }
    ]
  },
  {
    "changes": [
      {
        "principal": "aconcagua@mycompany.com",
        "add": [
          "EXECUTE"
        ]
      }
    ]
  }
]


def test_uc_permission_unroll():
    unrolled_changes = _mk_unrolled_changes(ref_changes_2)
    assert unrolled_changes == ref_unrolled_changes

