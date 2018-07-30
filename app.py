from flask import Flask, request, make_response
from json import dumps
import requests
from operator import itemgetter
from collections import OrderedDict

app = Flask(__name__)

# getting the response
def get_aws_data():
    aws_url = "https://s3-eu-west-1.amazonaws.com/styl-reading-list/data.json"
    response = requests.get(aws_url)
    return response.json()

# to get pretty print json format
def jsonify(status=200, indent=4, **kwargs):
    response = make_response(dumps(kwargs, indent=indent))
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    response.headers['mimetype'] = 'application/json'
    response.status_code = status
    return response

@app.route('/')
def hello_world():
    msg = {'msg': "Welcome to Reading List Be API homepage. End points details:",
    'endpoint1': "Endpoint /readlist/api/v1/books returns a collection of books",
    'endpoint1_sort': "Endpoint /readlist/api/v1/books capable of returning data "
                      "sorted by publication date(published_at)/title(name), asc and desc",
    'endpoint2': "Endpoint /readlist/api/v1/authors returns a collection of authors, "
                 "each author item contains collection of their books"}
    return jsonify(**msg)


@app.route('/readlist/api/v1/books')
def books_api_v1():
    aws_data = get_aws_data()
    sort = request.args.get('sort')
    if sort:
        order = request.args.get('order')
        if order:
            order = order.upper()
        if sort in ['published_at', "name"]:
            aws_data['books'] = sorted(aws_data['books'], key=itemgetter(sort), reverse=True if order == 'DESC' else False)
        else:  # as the req is for only 2 sorting keys, making sure other does not sort if passed in url
            aws_data = {'msg' : 'Sorting key <{}> is not supported.'
                        'Please use only one of the sorting keys(sort=published_at or sort=name)'.format(sort)}
    # print(sort,order)
    return jsonify(**aws_data)


@app.route('/readlist/api/v1/authors')
def authors_api_v1():
    aws_data = get_aws_data()
    # first creating unique list of all authors, Mrs is obvoiusly consdered as one and rest of them ignoring Dr, Mr or Prof
    # unique list = [Mrs. John Doe, John Doe, Jane Doe]
    author_list = list(set([auth['author'] if 'Mrs' in auth['author'] else
                       'Mr. ' + ' '.join(auth['author'].split()[1:]) for auth in aws_data['books']]))
    ord_dict = OrderedDict()
    # creating a python collection/dictionary of authors
    authors_dict = dict()
    authors_dict['authors'] = list()
    # first authors dictionary is populated with author collectons, 3 in this case
    for val in author_list:
        ord_dict = OrderedDict()
        ord_dict['name'] = val
        authors_dict['authors'].append(ord_dict)
    # for every author we are generating book collection associated to tht author
    for author in authors_dict['authors']:
        if author.get('books'):
            continue
        else:
            author['books'] = []
            # to ensure only unique book entry for gievn author is recorded
            for i, book_col in enumerate(aws_data['books']):
                if 'Mrs.' in author['name']:
                    if book_col['author'] == author['name']:
                        author['books'].append(aws_data['books'][i])
                    else:
                        continue
                elif 'Mrs.' not in author['name'] and 'Mrs.' not in book_col['author'] and book_col['author'].split()[1:] == \
                        author['name'].split()[1:]:
                    author['books'].append(aws_data['books'][i])
    return jsonify(**authors_dict)


@app.errorhandler(404)
def page_not_found(e):
    return jsonify(error=404, text=str(e)), 404


@app.errorhandler(500)
def page_not_found(e):
    msg = "Oppsie...This is embarrassing... something went wrong, we will be right back!!!"
    return jsonify(error=500, text=msg), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0')
