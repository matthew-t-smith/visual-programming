import json
import csv
import inspect

from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from rest_framework.decorators import api_view
from pyworkflow import Workflow, WorkflowException, Node
from drf_yasg.utils import swagger_auto_schema

fs = FileSystemStorage(location=settings.MEDIA_ROOT)


@swagger_auto_schema(method='get',
                     operation_summary='Create a new workflow.',
                     operation_description='Creates a new workflow with empty DiGraph.',
                     responses={
                         200: 'Created new DiGraph'
                     })
@api_view(['GET'])
def new_workflow(request):
    """Create a new workflow.

    Initialize a new, empty, NetworkX DiGraph object and store it in the session.

    Return:
        200 - Created new DiGraph
    """
    # Create new Workflow
    workflow = Workflow()
    # Save to session
    request.session.update(workflow.to_session_dict())
    data = workflow.to_graph_json()
    return JsonResponse(data)


@swagger_auto_schema(method='post',
                     operation_summary='Open workflow from file.',
                     operation_description='Loads a JSON file from disk and translates into Workflow object and JSON object of front-end',
                     responses={
                         200: 'Workflow representation in JSON',
                         400: 'No file specified',
                         404: 'File specified not found or not JSON graph'
                     })
@api_view(['POST'])
def open_workflow(request):
    """Open a workflow.

    User uploads a JSON file to the front-end that passes JSON data to be
    parsed and validated on the back-end.

    Args:
        request: Django request Object, should follow the pattern:
            {
                react: {react-diagrams JSON},
                networkx: {networkx graph as JSON},
            }

    Raises:
        JSONDecodeError: invalid JSON data
        KeyError: request missing either 'react' or 'networkx' data
        WorkflowException: error loading JSON into NetworkX DiGraph

    Returns:
        200 - JSON response with data.
        400 - No file specified
        404 - File specified not found, or not JSON graph
        500 - Missing JSON data or
    """
    try:
        combined_json = json.loads(request.body)

        workflow = Workflow.from_request(combined_json['networkx'])
        react = combined_json['react']
    except KeyError as e:
        return JsonResponse({'open_workflow': 'Missing data for ' + str(e)}, status=500)
    except json.JSONDecodeError as e:
        return JsonResponse({'No React JSON provided': str(e)}, status=500)
    except WorkflowException as e:
        return JsonResponse({e.action: e.reason}, status=404)

    # Construct response
    data = {
        'react': react,
        'networkx': workflow.to_graph_json(),
    }

    # Save Workflow info to session
    request.session.update(workflow.to_session_dict())
    return JsonResponse(data)


@swagger_auto_schema(method='post',
                     operation_summary='Save workflow to JSON file',
                     operation_description='Saves workflow to JSON file for download.',
                     responses={
                         200: 'Workflow representation in JSON',
                         400: 'No file specified',
                         404: 'File specified not found or not JSON graph'
                     })
@api_view(['POST'])
def save_workflow(request):
    """Save workflow.

    Saves a workflow to disk.

    Args:
        request: Django request Object

    Returns:
        Downloads JSON file representing graph.
    """
    # Retrieve stored workflow
    workflow = Workflow.from_session(request.session)

    # Check for existing graph
    if workflow.graph is None:
        return JsonResponse({'message': 'No graph exists.'}, status=404)

    # Load session data into Workflow object. If successful, return
    # serialized graph
    try:
        combined_json = json.dumps({
            'react': json.loads(request.body),
            'networkx': workflow.to_graph_json(),
        })

        response = HttpResponse(combined_json, content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename=%s' % workflow.file_path
        return response
    except json.JSONDecodeError as e:
        return JsonResponse({'No React JSON provided': str(e)}, status=500)
    except WorkflowException as e:
        return JsonResponse({e.action: e.reason}, status=404)


@swagger_auto_schema(method='get',
                     operation_summary='Retrieve a list of installed Nodes',
                     operation_description='Retrieves a list of installed Nodes, in JSON.',
                     responses={
                         200: 'List of installed Nodes, in JSON',
                     })
@api_view(['GET'])
def retrieve_nodes_for_user(request):
    """Assembles list of Nodes accessible to workflows.

    Retrieve a list of classes from the Node module in `pyworkflow`.
    List is split into 'types' (e.g., 'IO' and 'Manipulation') and
    'keys', or individual command Nodes (e.g., 'ReadCsv', 'Pivot').
    """
    data = dict()

    # Iterate through node 'types'
    for parent in Node.__subclasses__():
        data[parent.__name__] = list()

        # Iterate through node 'keys'
        for child in parent.__subclasses__():
            # TODO: check attribute-scope is handled correctly
            child_node = {
                'name': child.name,
                'key': child.__name__,
                'type': parent.__name__,
                'num_in': child.num_in,
                'num_out': child.num_out,
                'color': child.color or parent.color,
                'doc': child.__doc__,
                'options': {**parent.DEFAULT_OPTIONS, **child.DEFAULT_OPTIONS},
            }

            data[parent.__name__].append(child_node)

    return JsonResponse(data)


def retrieve_csv(request, node_id):
    if request.method == 'GET':
        """
        Retrieves a CSV after the associated node execution and returns it as a json.
        Currently just using a demo CSV in workspace. 
        """
        # Create the HttpResponse object with the appropriate CSV header.
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'

        writer = csv.writer(response)
        writer.writerow(['First row', 'Foo', 'Bar', 'Baz'])
        writer.writerow(['Second row', 'A', 'B', 'C', '"Testing"', "Here's a quote"])

        return response
