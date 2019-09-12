import React from 'react'
import { FormSpy } from 'react-final-form'
import { connect } from 'react-redux'
import PropTypes from 'prop-types'
import { isEmpty, get } from 'lodash'
import {diff} from 'deep-object-diff'
import * as actions from '../modules/editor/actions'
import fieldSets from '../modules/editor/field-sets'

const debounce = 2000

const getSetRootValues = (values) => {
  const sets = ['indicators', 'periods', 'disaggregations', 'sectors', 'administratives']
  const ret = {...values}
  sets.forEach(fieldSet => {
    if(ret.hasOwnProperty(fieldSet)){
      delete ret[fieldSet]
    }
  })
  return ret
}
const customDiff = (oldObj, newObj) => {
  const difference = diff(getSetRootValues(oldObj), getSetRootValues(newObj))
  // override deep diff to take the entire updated array
  Object.keys(difference).forEach((key) => {
    if(typeof difference[key] === 'object'){
      difference[key] = newObj[key]
    }
  })
  return difference
}

const getRootValues = (values, sectionKey) => {
  const ret = {...values}
  if(fieldSets.hasOwnProperty(sectionKey)){
    fieldSets[sectionKey].forEach(set => {
      delete ret[set]
    })
  }
  return ret
}


class AutoSave extends React.Component {
  componentWillMount(){
    const { setName, sectionIndex, itemIndex } = this.props
    if(setName !== undefined){
      this.save()
    } else {
      this.lastSavedValues = getRootValues(this.props.values, `section${sectionIndex}`)
    }
  }
  componentWillReceiveProps(prevProps) {
    if(prevProps.values === this.props.values){
      return
    }
    if (this.timeout) {
      clearTimeout(this.timeout)
    }
    this.timeout = setTimeout(this.save, debounce)
  }

  save = () => {
    const { values, setName, itemIndex, sectionIndex } = this.props

    if(setName !== undefined && itemIndex !== undefined){
      const thisValues = get(values, `${setName}[${itemIndex}]`)
      if(!thisValues) return
      const savedValues = get(this.props.editorRdr[`section${sectionIndex}`].fields, `${setName}[${itemIndex}]`)
      const item = thisValues
      const difference = customDiff(savedValues, item)
      delete difference.disaggregationTargets
      if(setName === 'relatedProjects'){
        if (Object.keys(item).indexOf('relatedProject') === -1 && Object.keys(item).indexOf('relatedIatiId') === -1) return
      }
      // if difference is not empty AND the difference is not just the newly created item id inserted from ADDED_NEW_ITEM
      if (!isEmpty(difference)) {
        if(
          !(Object.keys(difference).indexOf('id') !== -1)
          && !(Object.keys(difference).length === 1 && Object.keys(difference)[0] === 'dimensionNames')
        ){
          if(!item.id){
            this.props.addSetItem(sectionIndex, setName, item)
          } else {
            this.props.editSetItem(sectionIndex, setName, itemIndex, item.id, difference)
          }
        }
      }
    } else {
      const rootValues = getRootValues(values, `section${sectionIndex}`)
      const difference = customDiff(this.lastSavedValues, rootValues)
      if(
        !isEmpty(difference)
        && !(Object.keys(difference).length === 1 && Object.keys(difference)[0] === 'publishingStatus')
      ){
        const isDiffOnlyCurrentImage = Object.keys(difference).length === 1 && Object.keys(difference)[0] === 'currentImage'
        this.props.saveFields(difference, sectionIndex, isDiffOnlyCurrentImage)
        this.lastSavedValues = {
          ...this.lastSavedValues,
          ...difference
        }
      }
    }
  }

  render() {
    return null
  }
}
AutoSave.propTypes = {
  itemIndex: PropTypes.number,
  setName: PropTypes.string,
  sectionIndex: PropTypes.number
}

export default props => (
  <FormSpy {...props} subscription={{ values: true }} component={connect(({ editorRdr }) => ({ editorRdr }), actions)(AutoSave)} />
)