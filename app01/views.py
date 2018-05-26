from django.shortcuts import render, redirect, HttpResponse
from utils.pay import AliPay
import json
import time


def ali():
    app_id = "2016091400509627"

    # POST
    notify_url = "http://linzetong.club:8804/page2/"

    # GET
    return_url = "http://linzetong.club:8804/page2/"

    merchant_private_key_path = "keys/pri"
    alipay_public_key_path = "keys/pub"

    alipay = AliPay(
        appid=app_id,
        app_notify_url=notify_url,
        return_url=return_url,
        app_private_key_path=merchant_private_key_path,
        alipay_public_key_path=alipay_public_key_path,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥
        debug=True,  # 默认False,
    )
    return alipay


def page1(request):
    if request.method == "GET":
        return render(request, 'page1.html')
    else:
        money = float(request.POST.get('money'))
        alipay = ali()
        # 生成支付的url
        query_params = alipay.direct_pay(
            subject="充气式韩红",  # 商品简单描述
            out_trade_no="x2" + str(time.time()),  # 商户订单号
            total_amount=money,  # 交易金额(单位: 元 保留俩位小数)
        )

        pay_url = "https://openapi.alipaydev.com/gateway.do?{}".format(query_params)

        return redirect(pay_url)


def page2(request):
    alipay = ali()
    if request.method == "POST":
        # 检测是否支付成功
        # 去请求体中获取所有返回的数据：状态/订单号
        from urllib.parse import parse_qs

        # request.body                  => 字节类型
        # request.body.decode('utf-8')  => 字符串类型
        """
        {"k1":["v1"],"k2":["v1"]}
        k1=[v1]&k2=[v2]
        """
        body_str = request.body.decode('utf-8')
        post_data = parse_qs(body_str)
        # {k1:[v1,],k2:[v2,]}

        # {k1:v1}
        post_dict = {}
        for k, v in post_data.items():
            post_dict[k] = v[0]


        print(post_dict)
        """
        {'gmt_create': '2017-11-24 14:53:41', 'charset': 'utf-8', 'gmt_payment': '2017-11-24 14:53:48', 'notify_time': '2017-11-24 14:57:05', 'subject': '充气式韩红', 'sign': 'YwkPI9BObXZyhq4LM8//MixPdsVDcZu4BGPjB0qnq2zQj0SutGVU0guneuONfBoTsj4XUMRlQsPTHvETerjvrudGdsFoA9ZxIp/FsZDNgqn9i20IPaNTXOtQGhy5QUetMO11Lo10lnK15VYhraHkQTohho2R4q2U6xR/N4SB1OovKlUQ5arbiknUxR+3cXmRi090db9aWSq4+wLuqhpVOhnDTY83yKD9Ky8KDC9dQDgh4p0Ut6c+PpD2sbabooJBrDnOHqmE02TIRiipULVrRcAAtB72NBgVBebd4VTtxSZTxGvlnS/VCRbpN8lSr5p1Ou72I2nFhfrCuqmGRILwqw==', 'buyer_id': '2088102174924590', 'invoice_amount': '666.00', 'version': '1.0', 'notify_id': '11aab5323df78d1b3dba3e5aaf7636dkjy', 'fund_bill_list': '[{"amount":"666.00","fundChannel":"ALIPAYACCOUNT"}]', 'notify_type': 'trade_status_sync', 'out_trade_no': 'x21511506412.4733646', 'total_amount': '666.00', 'trade_status': 'TRADE_SUCCESS', 'trade_no': '2017112421001004590200343962', 'auth_app_id': '2016082500309412', 'receipt_amount': '666.00', 'point_amount': '0.00', 'app_id': '2016082500309412', 'buyer_pay_amount': '666.00', 'sign_type': 'RSA2', 'seller_id': '2088102172939262'}
        {'stade_status': "trade_success",'order':'x2123123123123'}
        """
        sign = post_dict.pop('sign', None)

        status = alipay.verify(post_dict, sign)
        print('POST验证', status)
        if status:
            print("post_dict['stade_status']: ", post_dict['stade_status'])
            print("post_dict['out_trade_no']: ", post_dict['out_trade_no'])

        return HttpResponse('POST返回')
    else:
        # QueryDict = {'k':[1],'k1':[11,22,3]}
        params = request.GET.dict()
        sign = params.pop('sign', None)
        status = alipay.verify(params, sign)
        print('GET验证', status)
        return HttpResponse('支付成功')