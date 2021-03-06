import { NodeModel } from '@projectstorm/react-diagrams';
import VPPortModel from '../VPPort/VPPortModel';

export default class CustomNodeModel extends NodeModel {

    constructor(options = {}, config = {}) {
        super({
            ...options,
            type: 'custom-node'
        });
        this.options.node_id = this.options.id;
        this.config = config;
        this.configParams = options.option_types;
        this.options.status = options.status || "unconfigured";

        // add flow control input port
        this.addPort(
            new VPPortModel({
                in: true,
                type: 'vp-port',
                name: 'flow-in'
            })
        );
        // if flow node, add flow control output port
        if (this.options.node_type === "flow_control") {
            this.addPort(
                new VPPortModel({
                    in: false,
                    type: 'vp-port',
                    name: 'flow-out'
                })
            );
        }
        const nIn = options.num_in === undefined ? 1 : options.num_in;
        const nOut = options.num_out === undefined ? 1 : options.num_out;
        // setup in and out ports
        for (let i = 0; i < nIn; ++i) {
            this.addPort(
                new VPPortModel({
                    in: true,
                    type: 'vp-port',
                    name: `in-${i}`
                })
            );
        }
        for (let i = 0; i < nOut; ++i) {
            this.addPort(
                new VPPortModel({
                    in: false,
                    type: 'vp-port',
                    name: `out-${i}`
                })
            );
        }
    }

    getNodeId() {
      return this.options.node_id;
    }

    serialize() {
        return {
            ...super.serialize(),
            options: this.options,
            config: this.config
        }
    }

    deserialize(ob, engine) {
        super.deserialize(ob, engine);
    }

    setStatus(status) {
        this.options.status = status;
    }
}
