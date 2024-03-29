import React from 'react'
import {
  Icon, Upload, Form, Button, Alert, Progress
} from 'antd'
import Cookies from 'js-cookie'
import { withTranslation } from 'react-i18next'
import { connect } from 'react-redux'

import InputLabel from '../../../../utils/input-label'
import actionTypes from '../../action-types'
import api from '../../../../utils/api'
import { getBase64 } from '../../../../utils/misc'

const { Item } = Form
class ProjectPhoto extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      loading: false,
      error: '',
      uploadingError: false,
      imageUrl: props.value,
      percent: 0
    }
  }
  componentWillReceiveProps(nextProps) {
    if (nextProps.value !== this.props.value) {
      setTimeout(() => {
        this.setState({
          imageUrl: nextProps.value
        })
      }, 100)
    }
  }
  handleChange = (info) => {
    if (info.hasOwnProperty('event')) {
      this.setState({
        percent: info.event.percent
      })
    }
    if (info.file.status === 'uploading') {
      getBase64(info.file.originFileObj, (imageUrl) => {
        this.setState({
          imageUrl,
          loading: true,
        })
      })
      return
    }
    if (info.file.status === 'error') {
      this.setState({
        uploadingError: true,
        loading: false
      })
    }
  }

  handleSuccess = (ev) => {
    this.props.dispatch({ type: actionTypes.SAVE_FIELDS, fields: { currentImage: ev.current_image }, sectionIndex: 1 })
    this.props.dispatch({ type: actionTypes.BACKEND_SYNC })
    setTimeout(() => {
      this.setState({
        loading: false
      })
    }, 1000)
  }

  beforeUpload = (file) => {
    const { t } = this.props
    const isImage = file.type === 'image/jpeg' || file.type === 'image/png'
    const isLt10M = file.size / 1000000 < 10
    if (!isImage) {
      this.setState({
        error: t('Please upload an image'),
        loading: false
      })
    } else if (!isLt10M) {
      this.setState({
        error: t('The uploaded file is too big'),
        loading: false
      })
    } else {
      this.setState({
        error: ''
      })
    }
    return isImage && isLt10M
  }

  deleteImage = () => {
    api.patch(`/project/${this.props.projectId}/`, {
      currentImage: null
    })
    this.setState({
      imageUrl: '',
      uploadingError: '',
      loading: false
    })
  }

  render() {
    const { t } = this.props
    return (
      <Item
        validateStatus={this.props.validateStatus}
        label={
          <InputLabel
            tooltip={t('Project photo tooltip')}
          >{t('Photo')}
          </InputLabel>}
      >
        {this.state.error &&
          <Alert type="error" message={this.state.error} style={{ marginBottom: 15 }} />
        }
        {this.state.imageUrl && (
          <div>
            <div className="uploaded-image">
              <img src={this.state.imageUrl} alt="" />
              {(this.state.loading || this.state.uploadingError) &&
                <div className="progress-overlay">
                  <Progress type="circle" percent={this.state.percent} {...Object.assign({}, this.state.uploadingError ? { status: 'exception' } : {})} />
                </div>
              }
            </div>
            <div>
              <Button icon="delete" onClick={this.deleteImage}>{t('Remove Image')}</Button>
            </div>
          </div>
        )}
        <div style={{ display: this.state.imageUrl === '' ? 'block' : 'none' }}>
          <Upload.Dragger
            showUploadList={false}
            name="current_image"
            listType="picture"
            action={`/rest/v1/project/${this.props.projectId}/?format=json`}
            method="PATCH"
            onChange={this.handleChange}
            onSuccess={this.handleSuccess}
            beforeUpload={this.beforeUpload}
            headers={{ 'X-CSRFToken': Cookies.get('csrftoken') }}
          >
            {this.state.loading && (
              <div>
                <p className="ant-upload-drag-icon">
                  <Icon type="loading" />
                </p>
                <p className="ant-upload-text">{t('Uploading')}...</p>
              </div>
            )}
            {!this.state.loading && (
              <div>
                <p className="ant-upload-drag-icon">
                  <Icon type="picture" theme="twoTone" />
                </p>
                <p className="ant-upload-text">{t('Drag file here')}</p>
                <p className="ant-upload-hint">{t('or click to browse from computer')}</p>
                <p><small>Max: 10MB</small></p>
              </div>
            )}
          </Upload.Dragger>
        </div>
      </Item>
    )
  }
}

export default withTranslation()(connect()(ProjectPhoto))
