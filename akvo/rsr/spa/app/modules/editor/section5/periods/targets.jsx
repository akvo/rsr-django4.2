import React from 'react'
import { connect } from 'react-redux'
import { isEqual, get } from 'lodash'
import FinalField from '../../../../utils/final-field'
import AutoSave from '../../../../utils/auto-save'

class DimensionTargets extends React.Component {
  shouldComponentUpdate(prevProps) {
    const { resultIndex, indicatorIndex } = this.props
    const path = `results[${resultIndex}].indicators[${indicatorIndex}].dimensionNames`
    return !isEqual(get(prevProps, path), get(this.props, path)) || prevProps.periodId !== this.props.periodId
  }
  render() {
    const { resultIndex, indicatorIndex, indicatorId, periodIndex, periodId, fieldName, formPush, atIndicator } = this.props
    const path = `results[${resultIndex}].indicators[${indicatorIndex}]`
    const indicator = get(this.props, path)
    if (!indicator) {
      return null
    }
    const { dimensionNames } = indicator
    let container
    if(atIndicator){
      container = indicator
    } else {
      container = indicator.periods[periodIndex]
    }
    if (container === undefined) {
      container = { indicator: indicatorId }
    }
    if (!container.disaggregationTargets) container.disaggregationTargets = []
    if (!dimensionNames || dimensionNames.length === 0) return null
    let newIndex = container.disaggregationTargets.length - 1
    return (
      <div className="disaggregation-targets">
        {dimensionNames.map(dimension => (
          <div className="disaggregation-target">
            <div className="ant-col ant-form-item-label target-name">Target value: <b>{dimension.name}</b></div>
            {dimension.values.map(value => {
              let targetIndex = container.disaggregationTargets.findIndex(it => it.dimensionValue === value.id)
              if (targetIndex === -1 && (periodId || atIndicator)) {
                newIndex += 1
                targetIndex = newIndex
              }
              // reducer updates values and overrides FinalForm's values. Next few lines prevent this
              // setTimeout(() => {
              //   const targetIndex1 = container.disaggregationTargets.findIndex(it => it.dimensionValue === value.id)
              //   if(atIndicator){
              //     if (targetIndex1 === -1 && indicatorId) {
              //       formPush(`${fieldName}.disaggregationTargets`, { indicator: indicatorId, dimensionValue: value.id })
              //     }
              //   } else {
              //     if (targetIndex1 === -1 && periodId) {
              //       formPush(`${fieldName}.disaggregationTargets`, { period: periodId, dimensionValue: value.id })
              //     }
              //   }
              // }, 100)
              return (
                <div className="value-row">
                  {/* <AutoSave sectionIndex={5} setName={`${fieldName}.disaggregationTargets`} itemIndex={targetIndex} /> */}
                  <div className="ant-col ant-form-item-label">{value.value}</div>
                  <FinalField
                    disabled={(!periodId && !atIndicator)}
                    name={`${fieldName}.disaggregationTargets[${targetIndex}].value`}
                    control="input"
                    withLabel
                    label={<span />}
                  />
                </div>
              )
            })}
          </div>
        ))}
      </div>
    )
  }
}

export default connect(({ editorRdr: { section5: { fields: { results } } } }) => ({ results }))(DimensionTargets)
