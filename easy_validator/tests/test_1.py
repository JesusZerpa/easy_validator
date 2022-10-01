import pytest

@pytest.fixture()
def app():
    from quart import Quart,request,jsonify
    from easy_validator import UtilValidator
    app = Quart(__name__)
    app.config.update({
        "TESTING": True,
    })
    util_validator=UtilValidator(framework="quart")
    @util_validator
    async def my_validator():
        util_validator.validate(await request.json,{
            "date":util_validator.is_isoformat(required=True)
            })
    # other setup can go here
    @app.route("/post",methods=["POST"])
    @my_validator
    async def post():
        return jsonify({})
        

    yield app

    # clean up / reset resources here

@pytest.fixture()
def client(app):
    return app.test_client()
@pytest.fixture()
def client(app):
    return app.test_client()





def test_isoformat():
    from easy_validator import util_validator,ValidationError

    util_validator.validate({
            "date":"2022-09-30T00:25:40.338953"
        },{
            "date":util_validator.is_isoformat(required=True)
        })
    assert True

def test_not_isoformat():
    from easy_validator import util_validator,ValidationError
    try:
        util_validator.validate({
            "date":"10:00"
        },
        {
            "date":util_validator.is_isoformat()
        })
    except ValidationError as e:
        assert True





@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
@pytest.mark.asyncio
async def test_request_example(client):
    response = await client.post("/post",json={
        "date":"2022-09-30T00:25:40.338953"
        })
    with  open("test.html","w") as f:
        f.write((await response.data).decode("utf-8"))
   
    assert response.status_code==200
   