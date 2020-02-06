import React from 'react'
import { connect } from 'react-redux'
import { Form } from 'antd'
import { Form as FinalForm } from 'react-final-form'
import arrayMutators from 'final-form-arrays'

import './styles.scss'
import { removeSetItem } from '../actions'
import SectionContext from '../section-context'
import { useFetch } from '../../../utils/hooks'
import { shouldUpdateSectionRoot } from '../../../utils/misc'
import Partners from './partners/partners'
import Access from './access'

const Section3 = ({ fields, errors, projectId }) => { // eslint-disable-line
  const [{ results }, loading] = useFetch('/typeaheads/organisations')
  return (
    <div className="partners view">
      <SectionContext.Provider value="section3">
        <Form layout="vertical">
          <FinalForm
            onSubmit={() => { }}
            initialValues={fields}
            subscription={{}}
            mutators={{ ...arrayMutators }}
            render={(renderProps) => {
              const {
                form: {
                  mutators: { push }
                }
              } = renderProps
              return (
                <div>
                  <Partners {... { renderProps, push, results, loading, errors }} />
                  <Access {...{projectId}} />
                </div>
              )
            }}
          />
        </Form>
      </SectionContext.Provider>
    </div>
  )
}

export default connect(
  ({ editorRdr: { projectId, section3: { fields, errors } }}) => ({ fields, errors, projectId }),
  { removeSetItem }
)(React.memo(Section3, shouldUpdateSectionRoot))
