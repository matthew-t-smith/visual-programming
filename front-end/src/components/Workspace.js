import React from 'react';
import { Row, Col } from 'react-bootstrap';
import createEngine, { DiagramModel } from '@projectstorm/react-diagrams';
import { CanvasWidget } from '@projectstorm/react-canvas-core';
import { CustomLinkFactory } from './CustomLink/CustomLinkFactory';
import { CustomNodeModel } from './CustomNode/CustomNodeModel';
import { CustomNodeFactory } from './CustomNode/CustomNodeFactory';
import '../styles/Workspace.css';


class Workspace extends React.Component {

    constructor(props) {
        super(props);
        this.engine = createEngine();
        this.engine.getNodeFactories().registerFactory(new CustomNodeFactory());
        this.engine.getLinkFactories().registerFactory(new CustomLinkFactory());
        this.model = new DiagramModel();
        this.engine.setModel(this.model);
    }

    render() {
        return (
            <Row className="Workspace">
                <Col xs={3} className="node-menu">
                    <div>Drag-and-drop nodes to build a workflow.</div>
                    <hr />
                    <b>I/O</b>
                    <ul>
                        <NodeMenuItem model={{type: 'readCsv'}} name="Read CSV"
                            numPortsIn={0} color="black" />
                    </ul>
                    <b>Manipulation</b>
                    <ul>
                        <NodeMenuItem model={{type: 'filter'}} name="Filter Rows"
                            color="red" />
                        <NodeMenuItem model={{type: 'pivot'}} name="Pivot Table"
                            color="blue" />
                        <NodeMenuItem model={{type: 'multi-in'}} name="Multiple Input Example"
                            numPortsIn={3} numPortsOut={1}
                            color="green" />
                    </ul>
                </Col>
                <Col xs={9}>
                    <div style={{position: 'relative', flexGrow: 1}}
                        onDrop={event => {
                            var data = JSON.parse(event.dataTransfer.getData('storm-diagram-node'));
                            var node = new CustomNodeModel(data);
                            var point = this.engine.getRelativeMousePoint(event);
                            node.setPosition(point);
                            this.model.addNode(node);
                            this.forceUpdate();
                        }}
                    onDragOver={event => {
                            event.preventDefault();
                    }}
                    >
                    <CanvasWidget className="diagram-canvas" engine={this.engine} />
                    </div>
                </Col>
            </Row>
        );
    }
}


function NodeMenuItem(props) {
    return (
        <li className="NodeMenuItem"
            draggable={true}
            onDragStart={event => {
                event.dataTransfer.setData(
                    'storm-diagram-node',
                    JSON.stringify(props));
            }}
            style={{ color: props.color }}>
            {props.name}
        </li>
    )
}

export default Workspace;
