import getopt
import sys
import requests

api_key = "DONORSCHOOSE"  # DEMO KEY
api_url = "https://api.donorschoose.org/common/json_feed.html"
api_sorting_options = {"urgency": 0, "poverty": 1, "cost": 2, "popularity": 4, "exploration": 5, "newest": 7}
api_states_available = ["CA"]
default_state = 'CA'
default_cost_min = 0
default_cost_max = 2000
cost_to_complete_allowed_range = range(default_cost_min, default_cost_max+1)
max_allowed_results = 5


def execute_user_query(query,
                       state=default_state,
                       max=max_allowed_results,
                       cost_to_complete_min=default_cost_min,
                       cost_to_complete_max=default_cost_max):
    """validate params, get the api response, and display the results"""
    validate_parameters(query, state, max, cost_to_complete_min, cost_to_complete_max)
    response = request_from_api(query, state)
    print_api_response(response)


def validate_parameters(query, state, max, cost_to_complete_min, cost_to_complete_max):
    """
    Ensure that all given parameters are legal and useable
    :param query: query string given by user
    :param state:
    :param max: max number of query results desired
    :param cost_to_complete_min: min project cost allowed in  query results
    :param cost_to_complete_max: max project cost allowed in  query results
    :return: no return. failures should exit
    """
    illegal_strings = ['state=', 'costToCompleteRange=', 'APIKey=', 'max=']
    istrs_used = []
    try:
        for istr in illegal_strings:
            if istr in query:
                istrs_used.add(istr)
        assert(len(istrs_used) == 0)
    except AssertionError:
        print("Sorry, [{}] is not allowed in your query".format(istrs_used))
        sys.exit(1)
    try:
        assert(state in api_states_available)
    except AssertionError:
        print("Sorry, [{}] is not valid. State searches are currently limited to\n{}".format(state, api_states_available))
        sys.exit(1)

    try:
        assert(cost_to_complete_min in cost_to_complete_allowed_range and cost_to_complete_max in cost_to_complete_allowed_range)
        assert(cost_to_complete_min <= cost_to_complete_max)
    except AssertionError:
        print("Sorry, the funding search must be within the range of 0 to 2000 dollars.")
        sys.exit(1)

    try:
        assert(max <= max_allowed_results)
    except AssertionError:
        print("Sorry, the maximum allowable result set is currently {}".format(max_allowed_results))
        sys.exit(1)


def request_from_api(query, state, max=5, cost_to_complete_min=0, cost_to_complete_max=2000):
    """
    Make the query to the DonersChoose API
    :param query: user supplied query
    :param state: limit results to a state
    :param max: limit the number of query results
    :param cost_to_complete_min: min project cost allowed in  query results
    :param cost_to_complete_max: max project cost allowed in  query results
    :return: return a response object from request.get()
    """
    paramdata = {"keywords": '"{}"'.format(query),
                 "state": state.upper(),
                 "costToCompleteRange": "{} TO {}".format(cost_to_complete_min, cost_to_complete_max),
                 "APIKey": api_key,
                 "max": max}
    response = requests.get(api_url, params=paramdata)
    print("Executed Query:\n{}".format(response.url))
    return response


def print_api_response(proposal):
    """display results of query"""
    if proposal.status_code is not 200:
        print("There was an error returned from the api. HTTP Status was [{}]".format(proposal.status_code))
        print("The query was:\n{}".format(proposal.url))
        sys.exit(3)
    try:
        json_response = proposal.json()
    except ValueError:
        print("Error decoding API's json response.")
    # for item in json_response:
    #     print(item)
    if len(json_response) == 0:
        print("Sorry, there were no matches for your query")
    funded_percents = []
    donor_counts = []
    completion_costs = []
    student_counts = []
    total_prices = []
    print("----\nTop {} query hits:\n----\n".format(len(json_response["proposals"])))
    for proposal in json_response["proposals"]:
        try:
            total_prices.append(float(proposal["totalPrice"]))
            student_counts.append(int(proposal["numStudents"]))
            completion_costs.append(float(proposal["costToComplete"]))
            donor_counts.append(int(proposal["numDonors"]))
            funded_percents.append(float(proposal["percentFunded"]))
            # TODO: gather/List the average totals for the following values (aggrgtd from all 5 of the listed proposals)
            # TODO: Percent Funded, Number of Donors, Cost To Complete, Number of Students, Total Price
            print("TITLE:\t\t{}\nDESCRIPTION:\t{}\nURL:\t\t{}\nCOST TO COMPLETE: ${}".format(
                proposal["title"], proposal["shortDescription"], proposal["proposalURL"], proposal["costToComplete"]
            ))
        except KeyError:
            print("[ERROR] reading a field from current item")
            pass  # missing a field?
        print("----\n")
    print("\nProject Averages:")
    print("{} {} {}".format(completion_costs, sum(completion_costs), float(len(completion_costs))))
    print("\tTotal price average:\t\t${}".format(sum(total_prices) / float(len(total_prices))))
    print("\tAverage # of Students:\t\t{}".format(round(sum(student_counts) / float(len(student_counts)))))
    print("\tAverage cost to complete:\t${}".format(sum(completion_costs) / float(len(completion_costs))))
    print("\tAverage # of doners:\t\t{}".format(round(sum(donor_counts) / float(len(donor_counts)))))
    print("\tAverage funded %:\t\t{}".format(sum(funded_percents) / float(len(funded_percents))))
    print()


def main(argv):
    """
    main should be passed only the parameters given by the user (e.g. sys.argv[1:] ignores the program name)
    :param argv: user supplied parameters documented below.
    :return: return (0) on success, (1) for exceptions (2) for bad parameters/input
    """
    # set default to be overridden
    query = "Harry Potter"
    # get lists
    try:
        opts, args = getopt.getopt(argv, "q:", ["query="])
        assert(len(opts) > 0)
    except (getopt.GetoptError, AssertionError):
        print('Usage:\tpython {} -q "search string" '.format(sys.argv[0]))
        print('[-q string]')
        print('[--query string]')
        print('Note: Multi-word search strings should be surrounded with quotes(")\n')
        sys.exit(2)
    # set parameters based on user input
    for opt, arg in opts:
        if opt in ['-q', '--query']:
            query=arg
        # elif opt in ['-s', '--state']:  # example of expanding search params along with adding "s:" and "state=" above
        #     state = arg
    execute_user_query(query)
    sys.exit(0)

if __name__ == "__main__":
    main(sys.argv[1:])
