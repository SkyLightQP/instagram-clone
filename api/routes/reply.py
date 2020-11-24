import json

from rest_framework.response import Response
from rest_framework.views import APIView

from ..errors import VALIDATION_ERROR
from ..forms import ReplyForm
from ..models import Reply
from ..serializers import ReplySerializer
from ..utils import make_response_payload, require_token


class ReplyAPINotParams(APIView):
    @require_token
    def post(self, request):
        if request.META["CONTENT_TYPE"] != "application/json":
            return Response(make_response_payload(is_success=False), status=415)

        body = json.loads(request.body)
        form = ReplyForm(data=body)

        if not form.is_valid():
            return Response(make_response_payload(is_success=False, message=VALIDATION_ERROR), status=400)

        reply = Reply.objects.create(
            post_id_id=body["postId"],
            text=body["text"],
            user_id_id=request.user["user_id"]
        )

        return Response(make_response_payload(ReplySerializer(reply).data), status=200)


class ReplyAPI(APIView):
    @require_token
    def get(self, request, post_id):
        replies = Reply.objects.filter(post_id=post_id).all()

        result = []
        for value in replies:
            result.append(ReplySerializer(value).data)

        return Response(make_response_payload(result), status=200)
