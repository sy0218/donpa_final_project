from django.shortcuts import render
from .models import DonpaItem1
from .models import DonpaNews
from .models import DonpaEvent
from .models import InputList
from .models import InputList1
from .models import Goldprice


def item_list(request):
    items = DonpaItem1.objects.all()
    return render(request, 'index.html', {'items': items})

def aabata_view(request):
    # aabata.html 템플릿 렌더링
    items = InputList.objects.all()
    items1 = InputList1.objects.all()
    latest_goldprice = Goldprice.objects.latest('date')

    # 숫자 데이터를 텍스트로 변환
    
    sell_text = str(latest_goldprice.sell)
    buy_text = str(latest_goldprice.buy)

    return render(request, 'aabata.html', {'items': items, 
                                           'items1': items1, 
                                           'sell_text': sell_text,
                                           'buy_text': buy_text})

def events_view(request):
    # events.html 템플릿 렌더링
    items = DonpaEvent.objects.all()
    return render(request, 'event.html', {'items':items})    

def news_view(request):
    # news.html 템플릿 렌더링
    items = DonpaNews.objects.all()
    return render(request, 'news.html', {'items':items})


import pandas as pd
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def process_data(request):
    if request.method == 'POST':
        try:
            # POST 요청에서 데이터 추출
            data = json.loads(request.body.decode('utf-8'))
            selectedTitle = data['selectedTitle']
            selectedJobname = data['selectedJobname']
            selectedEmblem = data['selectedEmblem']
            sell = data['sell']
            buy = data['buy']
            year = data['year']
            month = data['month']
            day = data['day']
            day_name = data['day_name']

            # 데이터 프레임 생성
            df = pd.DataFrame({
                'title': [selectedTitle],
                'jobname': [selectedJobname],
                'emblem': [selectedEmblem],
                'sell': [sell],
                'buy': [buy],
                'year': [year],
                'month': [month],
                'day': [day],
                'day_name': [day_name]
            })

            # 여기에서 데이터프레임을 원하는 방식으로 처리
            df['sell'] = df['sell'].astype(float)
            df['buy'] = df['buy'].astype(float)
            df['year'] = df['year'].astype(int)
            df['month'] = df['month'].astype(int)
            df['day'] = df['day'].astype(int)

            # 데이터프레임 스케일링
            obj_col = df.select_dtypes(include='object').columns
            from sklearn.preprocessing import StandardScaler

            # 스케일러 불러오기
            import joblib
            sds = joblib.load('/home/user/donpa/pybo/scaler.pkl')

            df_sc = sds.transform(df.drop(columns = obj_col))
            df_sc = pd.DataFrame(df_sc, columns = df.drop(columns = obj_col).columns)

            # object 타입 컬럼 붙여주기
            for i in obj_col:
                df_sc[i] = df[i]

            # 원핫 인코딩 돌려주자
            from sklearn.preprocessing import OneHotEncoder
            encoder = joblib.load('/home/user/donpa/pybo/encoder.pkl')
            
            # 범주형 열만 선택
            obj_df = df_sc.select_dtypes(include='object')
            # 숫자형 열만 선택
            no_obj_df = df_sc.select_dtypes(exclude='object')
            # 범주형 열을 원핫 인코딩
            encoded_features = encoder.transform(obj_df)

            # 인코딩된 결과를 데이터프레임으로 변환
            encoded_df = pd.DataFrame(encoded_features.toarray(), columns=encoder.get_feature_names(obj_df.columns))
            # 인코딩된 범주형 열과 숫자형 열을 합침
            df_sc_encoding = pd.concat([no_obj_df[:len(df_sc)] , encoded_df[:len(df_sc)]], axis = 1)
            

            # 컬럼 특수문자 제거
            import re
            # 데이터프레임의 컬럼 이름에서 특수 문자를 제거하고 변경할 새로운 컬럼 이름 리스트 생성
            new_columns = []
            for old_column in df_sc_encoding.columns:
                new_column = re.sub(r'[^\w\s]', '', old_column)  # 특수 문자 제거
                new_columns.append(new_column)

            # 컬럼 이름을 새로운 이름으로 설정
            df_sc_encoding.columns = new_columns
            

            # 모델을 가져와 predict하자
            import xgboost as xgb
            xgb = joblib.load('/home/user/donpa/pybo/xg_model.pkl')
            pred_result = xgb.predict(df_sc_encoding)[0]

            pred_result = str(pred_result)
            
            # 결과를 JSON 형식으로 반환
            result = {'message': pred_result}
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({'message': 'Error: {}'.format(str(e))})
    else:
        return JsonResponse({'message': 'Invalid request method'})









import pandas as pd
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def process_data1(request):
    if request.method == 'POST':
        try:
            # POST 요청에서 데이터 추출
            data = json.loads(request.body.decode('utf-8'))
            selectedTitle = data['selectedTitle']
            selectedJobname = data['selectedJobname']
            selectedEmblem = data['selectedEmblem']
            sell = data['sell']
            buy = data['buy']
            year = data['year']
            month = data['month']
            day = data['day']
            day_name = data['day_name']

            # 데이터 프레임 생성
            df = pd.DataFrame({
                'title': [selectedTitle],
                'jobname': [selectedJobname],
                'emblem': [selectedEmblem],
                'sell': [sell],
                'buy': [buy],
                'year': [year],
                'month': [month],
                'day': [day],
                'day_name': [day_name]
            })

            # 여기에서 데이터프레임을 원하는 방식으로 처리
            df['sell'] = df['sell'].astype(float)
            df['buy'] = df['buy'].astype(float)
            df['year'] = df['year'].astype(int)
            df['month'] = df['month'].astype(int)
            df['day'] = df['day'].astype(int)

            # 데이터프레임 스케일링
            obj_col = df.select_dtypes(include='object').columns
            from sklearn.preprocessing import StandardScaler

            # 스케일러 불러오기
            import joblib
            sds = joblib.load('/home/user/donpa/pybo/sang_scaler.pkl')

            df_sc = sds.transform(df.drop(columns = obj_col))
            df_sc = pd.DataFrame(df_sc, columns = df.drop(columns = obj_col).columns)

            # object 타입 컬럼 붙여주기
            for i in obj_col:
                df_sc[i] = df[i]

            # 원핫 인코딩 돌려주자
            from sklearn.preprocessing import OneHotEncoder
            encoder = joblib.load('/home/user/donpa/pybo/sang_encoder.pkl')
            
            # 범주형 열만 선택
            obj_df = df_sc.select_dtypes(include='object')
            # 숫자형 열만 선택
            no_obj_df = df_sc.select_dtypes(exclude='object')
            # 범주형 열을 원핫 인코딩
            encoded_features = encoder.transform(obj_df)

            # 인코딩된 결과를 데이터프레임으로 변환
            encoded_df = pd.DataFrame(encoded_features.toarray(), columns=encoder.get_feature_names(obj_df.columns))
            # 인코딩된 범주형 열과 숫자형 열을 합침
            df_sc_encoding = pd.concat([no_obj_df[:len(df_sc)] , encoded_df[:len(df_sc)]], axis = 1)
            

            # 컬럼 특수문자 제거
            import re
            # 데이터프레임의 컬럼 이름에서 특수 문자를 제거하고 변경할 새로운 컬럼 이름 리스트 생성
            new_columns = []
            for old_column in df_sc_encoding.columns:
                new_column = re.sub(r'[^\w\s]', '', old_column)  # 특수 문자 제거
                new_columns.append(new_column)

            # 컬럼 이름을 새로운 이름으로 설정
            df_sc_encoding.columns = new_columns
            

            # 모델을 가져와 predict하자
            import xgboost as xgb
            xgb = joblib.load('/home/user/donpa/pybo/sang_xg_model.pkl')
            pred_result = xgb.predict(df_sc_encoding)[0]

            pred_result = str(pred_result)
            
            # 결과를 JSON 형식으로 반환
            result = {'message': pred_result}
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({'message': 'Error: {}'.format(str(e))})
    else:
        return JsonResponse({'message': 'Invalid request method'})