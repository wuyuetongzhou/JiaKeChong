import qiniu
from flask import current_app

access_key = "tsCfIrHr3qcsqYwsFcP14wiX0SlZDIHjX8Q5cSCe"
secret_key = "33w-yYHxdB__x8iv8R25kVUvobm2vu01AsF0wDxj"


def qiniu_image_store(data):
    # 创建鉴权对象
    q = qiniu.Auth(access_key, secret_key)
    # key 上传的图片名称 不指明让七牛云给你生成一个唯一的图片名称
    # key = 'hello'
    bucket_name = "jiakechongzhineng"
    token = q.upload_token(bucket_name)
    try:
        ret, info = qiniu.put_data(token, None, data)
        if ret is not None and info.status_code == 200:
            # print(ret)
            print('All is OK-------------')
            # print(info)
            # 返回图片名称
            return ret["key"]
        else:
            print(info+'------------------------------------->')  # error message in info
    except Exception as e:
        current_app.logger.error(e)
        # 自己封装的工具类给被人用的时候需要将异常抛出不能私自解决
        raise e


if __name__ == '__main__':
    file = input("请输入图片路径:")
    with open(file, "rb") as f:
        qiniu_image_store(f.read())
