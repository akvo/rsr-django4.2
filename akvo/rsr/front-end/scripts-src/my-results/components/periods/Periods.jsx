/*
   Akvo RSR is covered by the GNU Affero General Public License.
   See more details in the license.txt file located at the root folder of the
   Akvo RSR module. For additional details on the GNU license please see
   < http://www.gnu.org/licenses/agpl.html >.
 */
import React from "react";
import PropTypes from "prop-types";
import Collapse, { Panel } from "rc-collapse";
import { connect } from "react-redux";
import update from "immutability-helper";

import * as alertActions from "../../actions/alert-actions";
import * as collapseActions from "../../actions/collapse-actions";

import { periodSelectToggle } from "../../actions/ui-actions";

import * as c from "../../const";

import {
    getPeriodsActualValue,
    getIndicatorsChildrenIds,
    getPeriodsChildrenIds
} from "../../selectors";

import { _, collapseId, hideMe } from "../../utils";

import Updates from "../updates/Updates";

import { collapseChange } from "../../actions/collapse-actions";

import PeriodHeader from "./PeriodHeader";

const PeriodSelect = ({ id, toggleCheckbox, isChecked }) => {
    // NOTE: the onChange event handler can't be used here because it fires too late and the event
    // for opening/closing the collapse panel will be triggered. However when using the onClick
    // handler React complains that the component isn't managed correctly, thus the noop onChange.
    return (
        <input
            id={id}
            type="checkbox"
            checked={isChecked ? "checked" : ""}
            onClick={toggleCheckbox}
            onChange={() => {}}
        />
    );
};
PeriodSelect.propTypes = {
    id: PropTypes.number.isRequired,
    toggleCheckbox: PropTypes.func.isRequired,
    isChecked: PropTypes.bool.isRequired
};

class Periods extends React.Component {
    static propTypes = {
        parentId: PropTypes.number.isRequired
    };

    constructor(props) {
        super(props);
        this.collapseChange = this.collapseChange.bind(this);
        this.openNewForm = this.openNewForm.bind(this);
        this.toggleCheckbox = this.toggleCheckbox.bind(this);
        this.hideMe = this.hideMe.bind(this);
        // concatenate this model's name with parent's ID
        this.state = { collapseId: collapseId(c.OBJECTS_PERIODS, this.props.parentId) };
    }

    openNewForm(newKey, data) {
        // Add the key for a new update to the list of open panels
        this.setState(
            { newKeys: update(this.state.newKeys, { $push: [newKey] }) },
            // Only when the activeKey state is committed do we update the updates model
            this.props.callbacks.updateModel(c.OBJECTS_UPDATES, data)
        );
    }

    activeKey() {
        return this.props.keys[this.state.collapseId];
    }

    collapseChange(activeKey) {
        collapseChange(this.state.collapseId, activeKey);
    }

    toggleCheckbox(e) {
        e.stopPropagation();
        const periodId = parseInt(e.target.id);
        periodSelectToggle(periodId);
    }

    hideMe(id) {
        return hideMe(c.OBJECTS_PERIODS, this.props.parentId, id);
    }

    renderPanels(periodIds) {
        return periodIds.map(id => {
            const { parentId, ui, page } = this.props;
            const period = this.props.periods.objects[id];
            const isChecked = new Set(this.props.ui[c.SELECTED_PERIODS]).has(id);
            const needsReporting =
                !period.is_locked && period._meta && period._meta.children.ids.length === 0;
            const indicator = this.props.indicators.objects[parentId]
            const isQuantative = indicator.type === c.INDICATOR_QUANTATIVE

            let className = this.hideMe(id) ? "hidePanel" : "";
            className += isChecked ? " periodSelected" : needsReporting ? " needsReporting" : "";

            return (
                <Panel
                header={<PeriodHeader period={period} toggleCheckbox={this.toggleCheckbox} is2scale={this.props.is2scale} />}
                    key={id}
                    showArrow={!page.mode.public || !isQuantative}
                    disabled={page.mode.public && isQuantative}
                    className={className}
                >
                    <Updates indicatorId={parentId} period={period} />{" "}
                </Panel>
            );
        });
    }

    render() {
        const periodIds = this.props.indicatorChildrenIds[this.props.parentId];
        if (!this.props.periods.fetched) {
            return (
                <p className="loading">
                    Loading <i className="fa fa-spin fa-spinner" />
                </p>
            );
        } else if (periodIds.length > 0) {
            return (
                <div className={c.OBJECTS_PERIODS}>
                    <Collapse activeKey={this.activeKey()} onChange={this.collapseChange}>
                        {this.renderPanels(periodIds)}
                    </Collapse>
                </div>
            );
        } else {
            return (
                <div className="emptyData">
                    <p>No periods</p>
                </div>
            );
        }
    }
}

const mapStateToProps = store => {
    return {
        page: store.page,
        periods: store.models.periods,
        indicators: store.models.indicators,
        keys: store.keys,
        user:
            store.models.user.ids && store.models.user.ids.length > 0
                ? store.models.user.objects[store.models.user.ids[0]]
                : {},
        ui: store.ui,
        indicatorChildrenIds: getIndicatorsChildrenIds(store),
        periodChildrenIds: getPeriodsChildrenIds(store),
        actualValue: getPeriodsActualValue(store)
    };
};

export default connect(
    mapStateToProps,
    { ...alertActions, ...collapseActions }
)(Periods);
