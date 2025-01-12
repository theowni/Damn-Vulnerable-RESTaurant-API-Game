from unittest.mock import MagicMock, patch

import pytest
from apis.auth.utils import RolesBasedAuthChecker
from db.models import User, UserRole
from fastapi import Depends, HTTPException


def test_RolesBasedAuthChecker_should_raise_403_http_exception_if_user_does_not_have_required_role():
    mock_user = User(role=UserRole.CUSTOMER)
    auth_checker = RolesBasedAuthChecker(
        required_roles=[UserRole.CHEF, UserRole.EMPLOYEE]
    )

    http_exception = False
    try:
        auth_checker(user=mock_user)
    except HTTPException as exception:
        http_exception = exception

    assert http_exception.status_code == 403


def test_RolesBasedAuthChecker_should_return_true_if_user_has_required_role():
    mock_user = User(role=UserRole.CHEF)
    auth_checker = RolesBasedAuthChecker(
        required_roles=[UserRole.CHEF, UserRole.EMPLOYEE]
    )
    result = auth_checker(user=mock_user)
    assert result is True
