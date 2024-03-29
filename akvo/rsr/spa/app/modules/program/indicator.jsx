/* global window, document */
import React, { useState, useRef, useEffect } from 'react'
import { Row, Col, Collapse } from 'antd'
import moment from 'moment'
import { setNumberFormat } from '../../utils/misc'
import TargetCharts from '../../utils/target-charts'
import ExpandIcon from './ExpandIcon'
import ProgramPeriod from './ProgramPeriod'
import { sizes } from './config'
import AggregationModal from './AggregationModal'

const Indicator = ({
  periods,
  type: indicatorType,
  targetValue: indicatorTarget,
  countryFilter,
  scoreOptions,
  targetsAt,
  cumulative,
}) => {
  const [pinned, setPinned] = useState(-1)
  const [openedItem, setOpenedItem] = useState(null)
  const [countriesFilter, setCountriesFilter] = useState([])
  const [activePeriod, setActivePeriod] = useState({
    popUp: false,
    period: null,
  })
  const listRef = useRef(null)
  const pinnedRef = useRef(-1)
  const tooltipRef = useRef(null)
  const disaggTooltipRef = useRef(null)

  const initActualValue = 0
  const indicatorActualValue = periods
    ?.filter((p) => cumulative
      ? (moment().isBetween(moment(p?.periodStart, 'DD/MM/YYYY'), moment(p?.periodEnd, 'DD/MM/YYYY')))
      : p
    )
    ?.reduce((total, currentValue) => total + currentValue.actualValue, initActualValue)
  let scrollingTransition
  let tmid

  const filterProjects = it => {
    if (countriesFilter.length === 0 && countryFilter.length === 0) return true
    if (countryFilter && countryFilter.length > 0) {
      return countryFilter.findIndex(_it => it.country && it.country.isoCode === _it) !== -1
    }
    return countriesFilter.findIndex(_it => it.country && it.country.isoCode === _it) !== -1
  }
  const _setPinned = (to) => {
    setPinned(to)
    pinnedRef.current = to
  }

  const handleAccordionChange = (index) => {
    setOpenedItem(index)
    _setPinned(Number(index))
    if (index != null) {
      const offset = 63 + (index * 75) + listRef.current.children[0].children[index].offsetParent.offsetTop
      clearTimeout(tmid)
      scrollingTransition = true
      window.scroll({ top: offset - sizes.stickyHeader.height, behavior: 'smooth' })
      tmid = setTimeout(() => {
        scrollingTransition = false
      }, 1000)
    }
  }

  const handleScroll = () => {
    if (pinnedRef.current !== -1 && !scrollingTransition && listRef.current.children[0].children[pinnedRef.current]) {
      const diff = (window.scrollY + sizes.stickyHeader.height) - (listRef.current.children[0].children[pinnedRef.current].offsetParent.offsetTop + 63 + (pinnedRef.current * 75))
      if (diff < -20 || diff > listRef.current.children[0].children[pinnedRef.current].clientHeight) {
        _setPinned(-1)
      }
    }
  }
  useEffect(() => {
    tooltipRef.current = document.getElementById('bar-tooltip')
    disaggTooltipRef.current = document.getElementById('disagg-bar-tooltip')
    document.addEventListener('scroll', handleScroll)
    return () => document.removeEventListener('scroll', handleScroll)
  }, [])
  return (
    <div className="indicator">
      {((targetsAt && targetsAt === 'indicator') && (indicatorTarget > 0)) && (
        <Row type="flex" justify="end" align="middle">
          <Col span={4} className="stats-indicator text-right">
            <div className="stat value">
              <div className="label">aggregated actual</div>
              <b>{setNumberFormat(indicatorActualValue)}</b><br />
              <span>
                of <b>{setNumberFormat(indicatorTarget)}</b> target
              </span>
            </div>
          </Col>
          <Col span={4}>
            <TargetCharts targetValue={indicatorTarget} actualValue={indicatorActualValue} />
          </Col>
        </Row>
      )}
      <Collapse expandIcon={({ isActive }) => <ExpandIcon isActive={isActive} />}>
        {periods
          ?.sort((a, b) => moment(a.periodEnd, 'DD/MM/YYYY').format('YYYY') - moment(b.periodEnd, 'DD/MM/YYYY').format('YYYY'))
          ?.map((period, index) => {
            const filteredContributors = period.contributors.filter(filterProjects)
            const filteredCountries = countryFilter.length > 0 ? countryFilter : period.countries
            const aggFilteredTotal = filteredContributors.reduce((prev, value) => prev + value.actualValue, 0)
            const aggFilteredTotalTarget = filteredContributors.reduce((prev, value) => prev + (value.targetValue ? value.targetValue : 0), 0)
            const actualValue = countryFilter.length > 0 ? aggFilteredTotal : period.actualValue
            const targetValue = countryFilter.length > 0 ? aggFilteredTotalTarget : period.targetValue
            return (
              <ProgramPeriod
                key={index}
                {...{
                  listRef,
                  tooltipRef,
                  disaggTooltipRef,
                  period,
                  targetsAt,
                  indicatorType,
                  scoreOptions,
                  countryFilter,
                  filteredContributors,
                  filteredCountries,
                  actualValue,
                  targetValue,
                  aggFilteredTotalTarget,
                  aggFilteredTotal,
                  pinned,
                  countriesFilter,
                  openedItem,
                  periodIndex: index,
                  activePeriod,
                  setActivePeriod,
                  handleCountryFilter: setCountriesFilter,
                  handleAccordionChange
                }}
              />
            )
          })}
      </Collapse>
      {activePeriod?.period && (
        <AggregationModal
          {...activePeriod?.period}
          popUp={activePeriod?.popUp}
          handleOnOk={() => setActivePeriod({
            ...activePeriod,
            popUp: !activePeriod?.popUp
          })}
        />
      )
      }
    </div>
  )
}

export default Indicator
