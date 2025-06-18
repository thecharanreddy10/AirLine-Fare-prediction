from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.files.storage import default_storage
from mainapp.models import *
from userapp.models import *
from adminapp.models import *
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from datetime import datetime, timedelta

import pickle
import pandas as pd
import sklearn

import statistics

# Create your views here.
def user_dashboard(request):
    user_id = request.session.get("user_id")
    dbUser = UserDetails.objects.get(user_id = user_id)
    context = {
        "user": dbUser,
    }

    if request.method == 'POST':
        try:
            airline = float(request.POST.get('airline'))
            source_city = float(request.POST.get('source_city'))
            departure_time = float(request.POST.get('departure_time'))
            destination_city = float(request.POST.get('destination_city'))
            flight_class = float(request.POST.get('class'))
            stops = float(request.POST.get('stops'))
            days_left = float(request.POST.get('days_left'))

            print(f"{airline}, {source_city}, {departure_time}, {days_left}, {destination_city}, {flight_class}, {stops}")

            request.session["airline"] = airline
            request.session["source_city"] = source_city
            request.session["departure_time"] = departure_time
            request.session["days_left"] = days_left
            request.session["destination_city"] = destination_city
            request.session["flight_class"] = flight_class
            request.session["stops"] = stops

            route_details_list = get_route_flights(airline, source_city, departure_time, destination_city, flight_class, stops, days_left)
            print(f"route_details_list {route_details_list}")

            request.session["route_details_list"] = route_details_list

            return redirect('route_list')


        except (ValueError, TypeError):
            messages.warning(request, "Please enter valid numbers.")
            return redirect('user_dashboard')

    return render(request, 'user/user-dashboard.html', context)


###############       Flight Price Prediction CODE     #####################

def get_route_flights(airline, source_city, departure_time, destination_city, flight_class, stops, days_left):
    dataset = Datasets_Details.objects.last()
    df = pd.read_csv(dataset.dataset_name.path)


    filtered_records = df[
            (df['airline'] == airline) &
            (df['source_city'] == source_city) &
            (df['departure_time'] == departure_time) &
            (df['destination_city'] == destination_city) &
            (df['class'] == flight_class) &
            (df['stops'] == stops) &
            (df['days_left'] == days_left)
        ]
    
    if not filtered_records.empty:
        route_list = filtered_records.to_dict(orient='records')
        print(f"list_lenght -------------- {len(route_list)}")
    else:
        route_list = []
    return route_list

def get_next_days_analysis(airline, source_city, departure_time, stops, arrival_time, destination_city, flight_class, duration, days_left):

    next_days_prediction_price_list = []
    difference_list = [1, 6, 11, 16, 21, 26, 31, 36, 41, 46]
    
    for i in range(0,10):
        days_left = difference_list[i]

        file_path = 'rf-cyber.pkl'

        with open(file_path, 'rb') as file:
            loaded_model = pickle.load(file)

        nxt_prediction_price = loaded_model.predict([[airline, source_city, departure_time, stops, arrival_time, destination_city, flight_class, duration, days_left]])

        nxt_prediction_result = int(nxt_prediction_price[0])

        next_days_prediction_price_list.append(nxt_prediction_result)

    return next_days_prediction_price_list

def detection_dashboard(request): 

    airline = request.session.get('airline')
    source_city = request.session.get('source_city')
    departure_time = request.session.get('departure_time')
    stops = request.session.get('stops')
    arrival_time = request.session.get('arrival_time')
    destination_city = request.session.get('destination_city')
    flight_class = request.session.get('class')
    duration = request.session.get('duration')
    days_left = request.session.get('days_left')

    nxt_analysis  = get_next_days_analysis(airline, source_city, departure_time, stops, arrival_time, destination_city, flight_class, duration, days_left)
    print(f"nxt-analysis {nxt_analysis}")

    dataset = Datasets_Details.objects.last()
    df = pd.read_csv(dataset.dataset_name.path)

    filtered_route_records = df[
            (df['airline'] == airline) &
            (df['source_city'] == source_city) &
            (df['destination_city'] == destination_city) &
            (df['class'] == flight_class)
        ]
    
    if not filtered_route_records.empty:
        route_price_list = filtered_route_records['price'].tolist()

        max_price = max(route_price_list)
        min_price = min(route_price_list)
        avg_price = round(statistics.mean(route_price_list),2)

        print(f"Route Prices List: {route_price_list}")
        print(f"Max Price: {max_price}")
        print(f"Min Price: {min_price}")
        print(f"Average Price: {avg_price}")
    else:
        route_price_list = []
        max_price = None
        min_price = None
        avg_price = None  # Optional: Handle empty list case

    context = {
        'nxt_analysis': nxt_analysis,
        'max_price': max_price,
        'min_price': min_price,
        'avg_price': avg_price
    }

    return render(request, 'user/detection.html', context)


def route_list(request):

    airline = request.session.get("airline")
    source_city = request.session.get("source_city")
    departure_time = request.session.get("departure_time")
    arrival_time = request.session.get("arrival_time")
    destination_city = request.session.get("destination_city")

    route_list = request.session.get("route_details_list")


    if request.method == 'POST':
        try:
            airline = float(request.POST.get('airline'))
            source_city = float(request.POST.get('source_city'))
            departure_time = float(request.POST.get('departure_time'))
            stops = float(request.POST.get('stops'))
            arrival_time = float(request.POST.get('arrival_time'))
            destination_city = float(request.POST.get('destination_city'))
            flight_class = float(request.POST.get('flight_class'))
            duration = float(request.POST.get('duration'))
            days_left = float(request.POST.get('days_left'))

            print(f"specific route details ---------- {airline}, {source_city}, {departure_time}, {stops}, {arrival_time}, {destination_city}, {flight_class}, {duration}, {days_left}")

        except (ValueError, TypeError):
            messages.warning(request, "Please enter valid numbers.")
            return redirect('route_list')
        
        file_path = 'rf-cyber.pkl'  # Update with your model file path
        try:
            with open(file_path, 'rb') as file:
                loaded_model = pickle.load(file)

            # Validate the model type
            if not isinstance(loaded_model, sklearn.base.BaseEstimator):
                messages.error(request, "Loaded model is not compatible.")
                return redirect("route_list")  # Redirect back to the form page

        except FileNotFoundError:
            messages.error(request, "Model file not found.")
            return redirect("route_list")  # Redirect back to the form page
        except AttributeError as e:
            messages.error(request, f"Model loading error: {str(e)}")
            return redirect("route_list")  # Redirect back to the form page

        prediction = loaded_model.predict([[airline, source_city, departure_time, stops, arrival_time, destination_city, flight_class, duration, days_left]])

        prediction_result = int(prediction[0])
        request.session['prediction_result'] = prediction_result

        request.session['airline'] = airline
        request.session['source_city'] = source_city
        request.session['departure_time'] = departure_time
        request.session['stops'] = stops
        request.session['arrival_time'] = arrival_time
        request.session['destination_city'] = destination_city
        request.session['class'] = flight_class
        request.session['duration'] = duration
        request.session['days_left'] = days_left

        print(f"prediction_result: {prediction_result}")
        messages.success(request, 'Prediction Successfull')
        return redirect("detection_result")
    

    context = {
        'airline': airline,
        'source_city': source_city,
        'departure_time': departure_time,
        'arrival_time': arrival_time,
        'destination_city': destination_city,
        'fl_details_list': route_list or [],
    }

    return render(request, 'user/routeList.html', context)



def detection_result(request):
    # Retrieve prediction criteria from session
    prediction_result = request.session.get('prediction_result', None)

    if not prediction_result:
        messages.error(request, "Prediction criteria not found.")
        return redirect('detection_dashboard')

    dataset = Datasets_Details.objects.last()

    try:
        # Read the CSV file
        df = pd.read_csv(dataset.dataset_name.path)

        # Extract filtering criteria
        airline = request.session.get('airline')
        source_city = request.session.get('source_city')
        departure_time = request.session.get('departure_time')
        stops = request.session.get('stops')
        arrival_time = request.session.get('arrival_time')
        destination_city = request.session.get('destination_city')
        flight_class = request.session.get('class')
        duration = request.session.get('duration')
        days_left = request.session.get('days_left')

        # Filter the dataset based on criteria
        filtered_records = df[
            (df['airline'] == airline) &
            (df['source_city'] == source_city) &
            (df['departure_time'] == departure_time) &
            (df['stops'] == stops) &
            (df['arrival_time'] == arrival_time) &
            (df['destination_city'] == destination_city) &
            (df['class'] == flight_class) &
            (df['duration'] == duration) &
            (df['days_left'] == days_left)
        ]


        # Get prediction price(s) or set an error message if none found
        if not filtered_records.empty:
            previous_price_list = filtered_records['price'].tolist()
            previous_price = previous_price_list[0]

            request.session['previous_price'] = previous_price

            print(f"Filtered Prices: {previous_price_list}")
            print(f"Previous Price: {previous_price}")
        else:
            previous_price = "No matching records found."
    except Exception as e:
        messages.error(request, f"Error reading dataset: {e}")
        return redirect('detection_dashboard')

    # Pass the prediction result to the template
    price_difference = abs(prediction_result - previous_price)
    print(f"price_difference: {price_difference}")
    context = {
        "prediction_price": prediction_result,
        "previous_price": previous_price,
        "price_difference": price_difference
    }
    return render(request, 'user/detection-result.html', context)


def user_profile(request):
    user_id = request.session["user_id"]
    dbUser = UserDetails.objects.get(user_id = user_id)

    if  request.method == "POST":
        
        user_name = request.POST.get('fullname')
        user_email = request.POST.get('email')
        user_password = request.POST.get('password')
        user_phone = request.POST.get('phone')
        user_age = request.POST.get('age')
        user_address = request.POST.get('address')

        if len(request.FILES) != 0:
            user_image = request.FILES['profileImg']
            dbUser.user_image = user_image
            dbUser.full_name = user_name
            dbUser.email = user_email
            dbUser.password = user_password
            dbUser.phone_number = user_phone
            dbUser.age = user_age
            dbUser.address = user_address

            dbUser.save()
            messages.success(request, "Profile Updated Successfully")
        else:
            dbUser.full_name = user_name
            dbUser.email = user_email
            dbUser.password = user_password
            dbUser.phone_number = user_phone
            dbUser.age = user_age
            dbUser.address = user_address

            dbUser.save()
            messages.success(request, "Profile Updated Successfully")


    context = {
        "user": dbUser
    }
    return render(request, 'user/profile.html', context)

def user_feedback(request):
    user_id = request.session["user_id"]
    dbUser = UserDetails.objects.get(user_id = user_id)
    if request.method == "POST":
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        sid = SentimentIntensityAnalyzer()
        score = sid.polarity_scores(comment)
        sentiment=None
        if score['compound']>0 and score['compound']<=0.5:
            sentiment='positive'
        elif score['compound']>=0.5:
            sentiment='very positive'
        elif score['compound']<-0.5:
            sentiment='negative'
        elif score['compound']<0 and score['compound']>=-0.5:
            sentiment='very negative'
        else :
            sentiment='neutral'
        Feedback.objects.create(Rating=rating,  Review=comment, Sentiment=sentiment, Reviewer=dbUser)
        messages.success(request, 'Feedback recorded successfully')
    return render(request, 'user/feedback.html')

def about_models(request):
    return render(request, 'user/aboutModels.html')

def user_about(request):
    return render(request, 'user/user_about.html')

def user_logout(request):
    request.session.flush()
    messages.success(request, 'You are Logged Out Successfully')
    return redirect("user_login")


