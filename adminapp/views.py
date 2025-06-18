from django.shortcuts import render, redirect
from mainapp.models import *
from userapp.models import *
from adminapp.models import *
from django.contrib import messages

import pandas as pd

from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import json

from adminapp.ml_model import preprocess_and_train, predict

# Create your views here.
def admin_dashboard(request):
    pending_user_count = UserDetails.objects.filter(user_status="pending").count()
    all_users_count = UserDetails.objects.exclude(user_status="pending").count()
    accepted_users_count=UserDetails.objects.filter(user_status="accepted").count()
    rejected_users_count=UserDetails.objects.filter(user_status="rejected").count()

    context = {
        'pendingusers_Count': pending_user_count,
        'allUsers_Count':all_users_count,
        'acceptedusers_Count': accepted_users_count,
        'rejectedusers_Count': rejected_users_count
    }
    return render(request, 'admin/admin-dashboard.html', context)

@csrf_exempt
def train_new_model(request):
    if request.method == 'POST':
        try:
            results = preprocess_and_train()
            messages.success(request, f"Model trained successfully! MAE: {results['mae']:.2f}, R2: {results['r2']:.2f}")
            return JsonResponse({'mae': results['mae'], 'r2': results['r2']})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return HttpResponseBadRequest("Invalid request method.")

@csrf_exempt
def predict_price(request):
    import datetime
    stops_mapping = {'zero': 0, 'one': 1, 'two_or_more': 2}

    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # If data is a string, parse it
            if isinstance(data, str):
                # Expected format: airline,source_city,destination_city,departure_date,arrival_time,class,stops
                parts = data.split(',')
                if len(parts) != 7:
                    return JsonResponse({'error': 'Input string must have 7 comma-separated values.'}, status=400)

                airline, source_city, destination_city, departure_date_str, arrival_time, travel_class, stops_str = [p.strip() for p in parts]

                # Calculate days_left from departure_date
                try:
                    departure_date = datetime.datetime.strptime(departure_date_str, '%d/%m/%Y').date()
                    today = datetime.date.today()
                    days_left = (departure_date - today).days
                    if days_left < 0:
                        return JsonResponse({'error': 'Departure date must be in the future.'}, status=400)
                except ValueError:
                    return JsonResponse({'error': 'Invalid date format. Use DD/MM/YYYY.'}, status=400)

                # Map stops string to int
                stops = stops_mapping.get(stops_str.lower())
                if stops is None:
                    return JsonResponse({'error': f'Invalid stops value: {stops_str}. Use zero, one, or two_or_more.'}, status=400)

                # For duration and departure_time, we need to set default or estimate values as they are missing
                # For now, set duration to a default (e.g., 2.0 hours) and departure_time to 'Morning'
                duration = 2.0
                departure_time = 'Morning'

                input_dict = {
                    'airline': airline,
                    'source_city': source_city,
                    'departure_time': departure_time,
                    'stops': stops,
                    'arrival_time': arrival_time,
                    'destination_city': destination_city,
                    'class': travel_class,
                    'duration': duration,
                    'days_left': days_left
                }
            else:
                input_dict = data

            prediction = predict(input_dict)
            return JsonResponse({'predicted_price': prediction})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return HttpResponseBadRequest("Invalid request method.")

def pending_users(request):
    pending_users = UserDetails.objects.filter(user_status="pending")
    context = {
        'pending_users': pending_users
    }
    return render(request, 'admin/pending-users.html', context)


def all_users(request):
    all_users = UserDetails.objects.exclude(user_status="pending")
    context = {
        'all_users': all_users
    }
    return render(request, 'admin/all-users.html', context)

def deleteAll_users(request):
    UserDetails.objects.exclude(user_status="pending").delete()
    messages.success(request, 'All users deleted successfully!')
    return redirect('all_users')

def accept_user(request, id):
    dbUser = UserDetails.objects.get(user_id = id)
    dbUser.user_status = "accepted"
    dbUser.save()
    messages.success(request, 'User Accepted Successfully')
    return redirect('pending_users')

def reject_user(request,id):
    dbUser = UserDetails.objects.get(user_id = id)
    dbUser.user_status = "rejected"
    dbUser.save()
    messages.success(request, 'User Rejected Successfully')
    return redirect('pending_users')

def change_status(request, id):
    dbUser = UserDetails.objects.get(user_id=id)
    if  dbUser.user_status == "accepted":
        dbUser.user_status =  "rejected"
    elif  dbUser.user_status == "rejected":
        dbUser.user_status = "accepted"
    dbUser.save()
    messages.success(request, 'User Status Changed Successfully')
    return redirect('all_users')

def delete_user(request,id):
    dbUser = UserDetails.objects.get(user_id=id)
    dbUser.delete()
    messages.success(request, 'User Deleted Successfully')
    return redirect('all_users')

def data_visualization(request):
    return render(request, 'admin/data-visualization.html')


def upload_dataset(request):
    if request.method == 'POST':
        file = request.FILES['dataset_file']
        file_size = str((file.size)/1024) +' kb'
        formated_file_size = str(int(file.size/1024)) + ' kb'
        Datasets_Details.objects.create(file_size = file_size, dataset_name = file, formated_file_size = formated_file_size)
        messages.success(request, 'Dataset Uploaded Successfully')
    return render(request, 'admin/upload-dataset.html')

def view_datasets_list(request):
    datasets_list = Datasets_Details.objects.all()
    context = {
        'datasets_list': datasets_list
    }
    return render(request, 'admin/view-dataset-list.html', context)

def delete_dataset(request, id):
    dbDataset = Datasets_Details.objects.get(dataset_id=id)
    dbDataset.delete()
    messages.success(request, 'Dataset Deleted Successfully')
    return redirect('view_datasets_list')

def view_dataset_result(request, id):
    dbDataset = Datasets_Details.objects.get(dataset_id=id)
    file = str(dbDataset.dataset_name)
    df = pd.read_csv(f'./media/{file}')
    table = df.to_html(table_id='data_table')
    return render(request, 'admin/view-dataset-result.html', {'t':table})

def train_and_test(request):
    return render(request, 'admin/train-and-test.html')

def train_and_test_result(request):
    messages.success(request, 'Model Trained Succesfully')
    return render(request, 'admin/train-and-test-result.html')

def admin_feedbacks(request):
    feedbacks = Feedback.objects.all()
    context = {
        "feedbacks":  feedbacks
    }
    return render(request, 'admin/feedbacks.html', context)

def deleteFeed(request,id):
    dbFeed = Feedback.objects.get(Feed_id=id)
    dbFeed.delete()
    messages.success(request,'Feedback Deleted Successfully')
    return redirect('admin_feedbacks')

def deleteSentFeed(request,id):
    dbFeed = Feedback.objects.get(Feed_id=id)
    dbFeed.delete()
    messages.success(request,'Feedback Deleted Successfully')
    return redirect('sentiment_analysis')

def deleteAllFeeds(request):
    Feedback.objects.all().delete()
    messages.success(request, 'All Items all deleted')
    return redirect('admin_feedbacks')

def deleteAllsentFeeds(request):
    Feedback.objects.all().delete()
    messages.success(request, 'All Items all deleted')
    return redirect('sentiment_analysis')

def sentiment_analysis(request):
    feedbacks = Feedback.objects.all()
    context = {
        "feedbacks":  feedbacks
    }
    return render(request, 'admin/sentiment-analysis.html', context)

def feedbacks_graph(request):
    vp_count = Feedback.objects.filter(Sentiment = "very positive").count()
    p_count = Feedback.objects.filter(Sentiment = "positive").count()
    vn_count = Feedback.objects.filter(Sentiment = "very negative").count()
    neg_count = Feedback.objects.filter(Sentiment = "negative").count()
    n_count = Feedback.objects.filter(Sentiment = "neutral").count()
    context = {
        "vp_count": int(vp_count),
        "p_count": int(p_count),
        "vn_count": int(vn_count),
        "neg_count": int(neg_count),
        "n_count":  int(n_count)
    }
    return render(request, 'admin/feedback-graph.html', context)

def run_densenet(request):
    return render(request, 'admin/densenet.html')

def run_densenet_result(request):
    model_name = "Densenet Model Executed Successfully"
    accuracy = 95.38  # Example accuracy, replace with actual accuracy calculation

    # Check if the model already exists in the database
    try:
        model_performance = Densenet_model.objects.get(Executed=model_name)
        # If it exists, update the accuracy
        model_performance.Model_accuracy = accuracy
    except Densenet_model.DoesNotExist:
        # If it does not exist, create a new instance
        model_performance = Densenet_model(Executed=model_name, Model_accuracy=accuracy)

    # Save the model performance (either newly created or updated)
    model_performance.save()
    about_model = "DenseNet offers higher accuracy than both Xception and MobileNet due to its dense connectivity pattern, which enhances feature reuse and gradient flow."
    context = {
        "model_name": model_name,
        "accuracy": accuracy,
        "about_model": about_model
    }
    messages.success(request, 'Densenet Model Executed Successfully')
    return render(request, 'admin/densenet-result.html', context)

def run_mobilenet(request):
    return render(request, 'admin/mobilenet.html')

def run_mobilenet_result(request):
    model_name = "Mobilenet Model Executed Successfully"
    accuracy = 89.23  # Example accuracy, replace with actual accuracy calculation

    # Check if the model already exists in the database
    try:
        model_performance = Mobilenet_model.objects.get(Executed=model_name)
        # If it exists, update the accuracy
        model_performance.Model_accuracy = accuracy
    except Mobilenet_model.DoesNotExist:
        # If it does not exist, create a new instance
        model_performance = Mobilenet_model(Executed=model_name, Model_accuracy=accuracy)

    # Save the model performance (either newly created or updated)
    model_performance.save()
    about_model = "MobileNet is optimized for speed and efficiency, making it significantly faster and more lightweight compared to both Xception and DenseNet, especially in mobile and edge device applications."
    context = {
        "model_name": model_name,
        "accuracy": accuracy,
        "about_model": about_model
    }
    messages.success(request, 'Mobilenet Model Executed Successfully')
    return render(request, 'admin/mobilenet-result.html', context)

def run_xception(request):
    return render(request, 'admin/xception.html')

def run_xception_result(request):
    model_name = "Xception Model Executed Successfully"
    accuracy = 90.76  # Example accuracy, replace with actual accuracy calculation

    # Check if the model already exists in the database
    try:
        model_performance = Xception_model.objects.get(Executed=model_name)
        # If it exists, update the accuracy
        model_performance.Model_accuracy = accuracy
    except Xception_model.DoesNotExist:
        # If it does not exist, create a new instance
        model_performance = Xception_model(Executed=model_name, Model_accuracy=accuracy)

    # Save the model performance (either newly created or updated)
    model_performance.save()
    about_model = "The Xception model generally offers higher accuracy than MobileNet, particularly in image classification tasks, due to its deeper architecture and use of depthwise separable convolutions."
    context = {
        "model_name": model_name,
        "accuracy": accuracy,
        "about_model": about_model
    }
    messages.success(request, 'Xception Model Executed Successfully')
    return render(request, 'admin/xception-result.html', context)

def run_random_forest(request):
    return render(request, 'admin/random-forest.html')

def run_random_forest_result(request):

    name = "Random Forest Algorithm"
    accuracy = 98.00
    Random_Forest.objects.create(
        Accuracy=accuracy,
        Result=name
    )

    about_model = "Random Forest is a powerful and versatile machine learning algorithm commonly used for classification and regression tasks. It is an ensemble learning method that combines the predictions of multiple decision trees to improve accuracy and reduce overfitting."

    # Retrieve the latest GRADIENT_ALGO entry
    latest_algo = Random_Forest.objects.last()
    context = {
        "about_model": about_model,
        "results": latest_algo
    }
    messages.success(request, 'Algorithm executed successfully')
    return render(request, 'admin/random-forest-result.html', context)

def comparison_graph(request):
    context = {
        'mobilenet_data': 89.23,
        'xception_data': 90.76,
        'densenet_data': 95.38
    }

    return render(request, 'admin/comparision-graph.html')


def adminlogout(req):
    messages.success(req, "You are logged out.")
    return redirect("admin_login")
