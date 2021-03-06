import json
import os

import jwt
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.views import APIView

from ..errors import USER_ALREADY_EXISTS, USER_NOT_FOUND, VALIDATION_ERROR
from ..forms import RegisterForm, LoginForm
from ..models import User
from ..serializers import UserSerializer
from ..utils import make_response_payload, require_token


class Register(APIView):
    def post(self, request):
        if request.META["CONTENT_TYPE"] != "application/json":
            return Response(make_response_payload(is_success=False), status=415)

        body = json.loads(request.body)
        form = RegisterForm(data=body)

        if not form.is_valid():
            return Response(make_response_payload(is_success=False, message=VALIDATION_ERROR), status=400)

        if User.objects.filter(email=body["email"]).exists():
            return Response(make_response_payload(is_success=False, message=USER_ALREADY_EXISTS), status=409)

        user = User.objects.create_user(email=body["email"], realname=body["realname"],
                                        username=body["username"],
                                        password=body["password"])

        result = UserSerializer(user).data

        return Response(make_response_payload(result), status=201)


class Login(APIView):
    def post(self, request):
        if request.META["CONTENT_TYPE"] != "application/json":
            return Response(make_response_payload(is_success=False), status=415)

        body = json.loads(request.body)
        form = LoginForm(data=body)

        if not form.is_valid():
            return Response(make_response_payload(is_success=False, message=VALIDATION_ERROR), status=400)

        user = authenticate(username=body["email"], password=body["password"])

        if user is None:
            return Response(make_response_payload(is_success=False, message=USER_NOT_FOUND), status=404)

        result = UserSerializer(user).data

        bjwt = jwt.encode({
            "uuid": result["user_id"],
            "email": result["email"]
        }, os.environ.get("SECRET_KEY"))

        data = {
            "user": result,
            "token": bjwt.decode("utf-8")
        }

        return Response(make_response_payload(data), status=200)


class Me(APIView):
    @require_token
    def get(self, request):
        return Response(make_response_payload(request.user), status=200)


class GetUser(APIView):
    @require_token
    def get(self, request, user_id):
        user = User.objects.get(user_id=user_id)
        return Response(make_response_payload(UserSerializer(user).data), status=200)

