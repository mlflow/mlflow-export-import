from mlflow_export_import.common.ws_permissions_utils import _map_acl_element, map_acl


# == Setup data

group_name_element = {
  "group_name": "admins",
  "all_permissions": [
    {
      "permission_level": "CAN_MANAGE",
      "inherited": True,
      "inherited_from_object": [
        "/directories/"
      ]
    }
  ]
}

user_name_element = {
  "user_name": "k2@karakoram.com",
  "all_permissions": [
    {
      "permission_level": "CAN_EDIT",
      "inherited": True,
      "inherited_from_object": [
        "/directories/"
      ]
    }
  ]
}

user_name_element_2 = {
  "user_name": "k2@karakoram.com",
  "all_permissions": [
    {
      "permission_level": "CAN_MANAGE",
      "inherited": False
    },
    {
      "permission_level": "CAN_MANAGE",
      "inherited": True,
      "inherited_from_object": [
        "/directories/767933989557963"
      ]
    }
  ]
}

mixed_acl = [ group_name_element, user_name_element ]
mixed_acl_2 = [ group_name_element, user_name_element_2 ]


# == Tests

def test_acl_element_group_name():
    acl2 = _map_acl_element(group_name_element)
    assert acl2 == [
      {
        "group_name": "admins",
        "permission_level": "CAN_MANAGE"
      }
    ]

def test_acl_element_user_name():
    acl2 = _map_acl_element(user_name_element)
    assert acl2 == [
      {
        "user_name": "k2@karakoram.com",
        "permission_level": "CAN_EDIT"
      }
    ]


def test_acl_element_user_name_2():
    acl2 = _map_acl_element(user_name_element_2)
    assert acl2 == [
      {
        "user_name": "k2@karakoram.com",
        "permission_level": "CAN_MANAGE"
      },
      {
        "user_name": "k2@karakoram.com",
        "permission_level": "CAN_MANAGE"
      }
    ]


def test_acl_mixed():
    assert map_acl(mixed_acl) == [
      {
        "group_name": "admins",
        "permission_level": "CAN_MANAGE"
      },
      {
        "user_name": "k2@karakoram.com",
        "permission_level": "CAN_EDIT"
      }
    ]


def test_acl_mixed_2():
    assert map_acl(mixed_acl_2) == [
      {
        "group_name": "admins",
        "permission_level": "CAN_MANAGE"
      },
      {
        "user_name": "k2@karakoram.com",
        "permission_level": "CAN_MANAGE"
      },
      {
        "user_name": "k2@karakoram.com",
        "permission_level": "CAN_MANAGE"
      }
    ]


def test_empty():
    assert map_acl({}) == []
