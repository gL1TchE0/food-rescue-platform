# Dispatcher Module

## What is the Dispatcher?

The dispatcher is the person responsible for managing food rescue deliveries. They can see all the tasks in the system, assign volunteers to pick up and deliver food, and monitor how things are going through a live dashboard.

## What the Dispatcher Can Do

- View all food rescue tasks across the platform
- Assign available volunteers to pending tasks
- Monitor live statistics like how many tasks are waiting, how many are in progress, and how many volunteers are online


## Who Can Access

Only users with the Dispatcher or Admin role can access these endpoints. All other roles such as Donor, Volunteer, and NGO are denied access.

Requests without a valid login token are also rejected.

## Dashboard Statistics

The dispatcher dashboard shows five key numbers. Pending tasks are the ones waiting to be assigned to a volunteer. Active tasks are the ones currently being picked up or delivered. Completed today shows how many tasks were finished on the current day. Online volunteers shows how many volunteers are currently available for assignments. Total volunteers shows the overall count of registered volunteers in the system.

## How Task Assignment Works

1. The dispatcher views the list of pending tasks
2. The dispatcher picks a task and selects an available volunteer
3. The system assigns the task to that volunteer and updates their status to busy
4. The volunteer receives a real-time notification about the new assignment
5. Other dispatchers are notified that the task has been assigned

## Testing

The dispatcher module has a dedicated test suite with 20 tests covering task viewing, access control, dashboard stats, and task assignment.

To run the tests:

    python -m pytest testing/test_dispatcher.py

Test results and details can be found in dispatcher_test_report.txt.

## Files

- backend/api/v1/dispatcher.py contains the dispatcher API endpoints
- testing/test_dispatcher.py contains the test suite with 20 tests
- dispatcher_test_report.txt contains the test results and documentation
