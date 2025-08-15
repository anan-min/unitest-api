GENERATE_UNIT_TEST_PROMPT = """
You are an expert software engineer specializing in writing comprehensive unit tests.

**Task**: Generate complete unit tests for the provided code.

**Requirements**:
1. Cover all functions and methods in the provided code.
2. Include edge cases and error scenarios.
3. Follow best practices for unit testing.
4. Make tests readable and maintainable.
5. Include proper imports and setup if needed.

**Source Code**:
{code}


**Instructions**:
- Analyze the provided code to determine the appropriate programming language and testing framework.
- Generate comprehensive unit tests that cover normal cases, edge cases, and error conditions.
- Use descriptive test names that explain what is being tested.
- Include assertions that verify the expected behavior.
- If the code has external dependencies, mock them appropriately.
- Provide only the test code, with no additional explanations.

**Response Format**: Provide only the complete, runnable unit test code.
"""


ts_example_code = """
import { Component, ElementRef, OnInit, ViewChild, ViewEncapsulation, OnDestroy, AfterViewInit } from '@angular/core'
import GSTC, { GSTCResult, Config } from 'gantt-schedule-timeline-calendar'
import { AppService } from 'src/app/services/app.service'
import { Plugin as TimelinePointer } from 'gantt-schedule-timeline-calendar/dist/plugins/timeline-pointer.esm.min.js'
import { EventSelection, Plugin as Selection } from 'gantt-schedule-timeline-calendar/dist/plugins/selection.esm.min.js'
import { Plugin as ItemResizing } from 'gantt-schedule-timeline-calendar/dist/plugins/item-resizing.esm.min.js'
import { Plugin as ItemMovement } from 'gantt-schedule-timeline-calendar/dist/plugins/item-movement.esm.min.js'
import { Plugin as HighlightWeekends } from 'gantt-schedule-timeline-calendar/dist/plugins/highlight-weekends.esm.min'
import { Plugin as CalendarScroll } from 'gantt-schedule-timeline-calendar/dist/plugins/calendar-scroll.esm.min.js'
// import { Plugin as CalendarScroll } from '../../shared/schedule/custom-plugins/calendar-scroll'
// import { Plugin as ItemMovement } from './itemMove.js'
import {
  ConfirmationService,
  MessageService,
  PrimeNGConfig,
  Message,
  ConfirmEventType,
  Confirmation,
} from 'primeng/api'
import { Schedule } from 'src/app/core/model/schedules'
import { IScheduleService } from 'src/app/core/services/schedule.service'
import { User } from 'src/app/core/model/user'
import { AxAuthenticationService } from '@atlasx/core/authentication'
import { Subscription } from 'rxjs'
import { NavbarService } from 'src/app/services/navbar.service'
import { ProjectService, UsersService } from 'src/app/services'
import { NewTask } from 'src/app/core/model/new-task'
import { ScheduleService } from 'src/app/services/schedule.service'
import { HolidayService } from 'src/app/services/holiday.service'
var workedOverlap: any = []

var holiday: any = {}
@Component({
  selector: 'app-calendar',
  templateUrl: './calendar.component.html',
  styleUrls: ['./calendar.component.scss'],
  providers: [ConfirmationService, MessageService],
  encapsulation: ViewEncapsulation.None,
})
export class CalendarComponent implements OnInit, OnDestroy, AfterViewInit {
  userInfo: User
  constructor(
    private appService: AppService,
    private confirmationService: ConfirmationService,
    private primengConfig: PrimeNGConfig,
    private messageService: MessageService,
    private scheduleService: ScheduleService,
    private authService: AxAuthenticationService,
    private navbarService: NavbarService,
    private projectService: ProjectService,
    private userService: UsersService,
    private holidayService: HolidayService
  ) {
    this.appService.activeMenu = 'calendar'
  }
  ngAfterViewInit(): void {
    this.scheduleService.updateState('config.chart.grid.cell.onCreate', (g) => {
      return [this.onCellCreate]
    })

    this.scheduleService.updateState('config.plugins', (g) => {
      return g.concat([
        TimelinePointer(),
        Selection(this.itemSelectOptions()),
        // ItemMovement(this.itemMove()),
        HighlightWeekends(),
      ])
    })
  }
  ngOnDestroy(): void {
    // alert('aaaaa')
    this.scheduleService.destroySchedule()
  }

  users: any[] = []
  schedules: any[] = []

  rowNotExists: any = {}

  cacheDateFilter: Date[] = [new Date(this.scheduleService.from), new Date(this.scheduleService.to)]

  teamLeader: User[] = []

  itemMove() {
    return {
      events: {
        onStart(onArg) {
          return onArg.items.after
        },
        onMove: (onArg) => {
        
          let a = JSON.parse(JSON.stringify(onArg.items.after[0]))
          onArg.items.after[0].style = { background: 'red' }
        
          return onArg.items.after
        },
        onEnd(onArg) {
          return []
        },
      },
    }
  }

  onCellCreate({ row, time, vido }) {
    let isOverlap = false

    const onClick = () => {
      // alert('click')
    }

    workedOverlap.forEach((d) => {
      if (time.leftGlobal >= d.start && time.leftGlobal < d.end && d.rowId === row.id.split('-')[1]) {
        isOverlap = true
      }
    })

    return vido.html`<div  @click="${onClick}"  style="width:100%; height:100%" class="${
      holiday[time.leftGlobal] ? 'holiday' : ''
    }">
    <div  style="width:100%; height:100%" class="${isOverlap ? 'workedOverlap' : ''}" ></div></div>`
  }

  ngOnInit(): void {
    this.holidayService
      .getHolidayByRange(this.scheduleService.from.toString(), this.scheduleService.to.toString())
      .subscribe((res: any) => {
        if (!res) return
        res.forEach((h) => {
          let dayTime = new Date(h.day).getTime()
          holiday[dayTime] = dayTime
        })
      })
    this.scheduleService.setPlugins([CalendarScroll()])
    this.authService.userInfos().subscribe((userInfo: any) => {
      this.userInfo = userInfo
    })
    this.navbarService.calendarSearchBarFilter$.subscribe((res) => {
      if (!res) return
    
      let filter = res.filters
      let query = res.query
      let dates = res.dates
      this.rowNotExists = {}

      let usersQuery = this.users

      if (
        dates &&
        !(
          this.cacheDateFilter[0].getTime() === dates[0].getTime() &&
          this.cacheDateFilter[1].getTime() === dates[1].getTime()
        )
      ) {
        this.cacheDateFilter = dates
        this.holidayService
          .getHolidayByRange(dates[0].getTime().toString(), dates[1].getTime().toString())
          .subscribe((res: any) => {
            if (!res) return
            res.forEach((h) => {
              let dayTime = new Date(h.day).getTime()
              holiday[dayTime] = dayTime
            })
            this.scheduleService.updateState('config.chart.time', (t) => {
              t.from = new Date(dates[0]).getTime()
              t.to = new Date(dates[1]).getTime()
              return t
            })
          })

        this.scheduleService
          .getAllSchedulesByRange({
            startDate: dates[0].getTime().toString(),
            endDate: dates[1].getTime().toString(),
            isUsers: true,
          })
          .subscribe((response) => {
            if (!response) return
            this.users = response.users
            this.schedules = response.schedules
          })
      }
      if (query) {
        let queryUser = query.trim().toLowerCase()
        usersQuery = usersQuery.filter((user) => {
          let exist =
            user.name.trim().toString().toLowerCase().includes(queryUser) ||
            user.surname.trim().toString().toLowerCase().includes(queryUser) ||
            user.position.trim().toString().toLowerCase().includes(queryUser)

          if (!exist) {
            this.rowNotExists[user.id] = user.id
          }

          return exist
        })
      }

      if (filter) {
        if (filter.teams.length > 0) {
          usersQuery = usersQuery.filter((user) => {
            let exist = filter.teams.includes(user.teamLeadId)
            if (!exist) {
              this.rowNotExists[user.id] = user.id
            }
            return exist
          })
        }

        if (filter.positions.length > 0) {
          let queryUser = query.trim().toLowerCase()
          usersQuery = usersQuery.filter((user) => {
            let exist = filter.positions.includes(user.position)
            if (!exist) {
              this.rowNotExists[user.id] = user.id
            }
            return exist
          })
        }
      }

      this.initRowsColumns(usersQuery)
    })
    this.userService.teamLead$.subscribe((res) => {
      if (!res) return
      this.teamLeader = res
    })
    this.messageService.add({ severity: 'success', summary: 'Confirmed', detail: 'Record deleted' })
    this.scheduleService
      .getAllSchedulesByRange({
        startDate: this.scheduleService.from.toString(),
        endDate: this.scheduleService.to.toString(),
        isUsers: true,
      })
      .subscribe((response) => {
        if (!response) return
        this.users = response.users
        this.schedules = response.schedules
        this.initRowsColumns()
      })
  }

  initRowsColumns(userParam?, schedulesParam?) {
    let users: any = userParam ? userParam : this.users
    let schedules: any = schedulesParam ? schedulesParam : this.schedules
    const rows = {}
    const items = {}

    let groupRows: any = {}
    users.forEach((user, index) => {
      if (!groupRows[user.teamLeadId]) {
        let teamName = this.teamLeader.find((u) => u.id === user.teamLeadId)?.name.toLowerCase()
        const id = GSTC.api.GSTCID('group-' + user.teamLeadId)
        rows[id] = {
          id,
          label: 'Team ' + teamName[0].toUpperCase() + teamName.slice(1),
          expanded: true,
          height: 20,
          classNames: ['team-highlight'],
        }
      }

      let name = user.name.toLowerCase()
      let lastNmae = user.surname.toLowerCase()
      const id = GSTC.api.GSTCID(user.id)

      rows[id] = {
        id,
        label: name[0].toUpperCase() + name.slice(1) + ' ' + lastNmae[0].toUpperCase() + lastNmae.slice(1),
        img: this.getParseInt(user.username)
          ? 'https://cdgisweb.cdg.co.th/telimage/PS' + user.username + '_01.jpg'
          : 'https://i.guim.co.uk/img/media/26392d05302e02f7bf4eb143bb84c8097d09144b/446_167_3683_2210/master/3683.jpg?width=1200&quality=85&auto=format&fit=max&s=a52bbe202f57ac0f5ff7f47166906403',
        availableHour: 40,
        expanded: false,
        position: user.position,
        height: 165,
        parentId: GSTC.api.GSTCID('group-' + user.teamLeadId),
        user: user,
      }
    })

    let workedOverlapItems: any[] = []
    for (let i = 0; i < schedules.length; i++) {
      let s1 = schedules[i]
      let s1Start = new Date(s1.startDate).getTime()
      let s1End = new Date(s1.endDate).getTime()
      for (let j = 1; j < schedules.length; j++) {
        let s2 = schedules[j]
        if (s1.id === s2.id) continue
        let s2Start = new Date(s2.startDate).getTime()
        let s2End = new Date(s2.endDate).getTime()

        let overlap
        if (s1.userId === s2.userId) {
          overlap =
            ((parseInt(s1.startTime) >= parseInt(s2.startTime) && parseInt(s1.startTime) < parseInt(s2.endTime)) ||
              (parseInt(s1.endTime) > parseInt(s2.startTime) && parseInt(s1.endTime) <= parseInt(s2.endTime))) &&
            ((s1Start >= s2Start && s1Start < s2End) || (s1End <= s2End && s1End > s2Start))
        }

        let start
        let end
        if (overlap) {
          start = s1Start > s2Start ? s1Start : s2Start
          end = s1End < s2End ? s1End : s2End
          workedOverlap.push({
            start,
            end,
            rowId: s1.userId,
          })
          workedOverlapItems.push(s1.id)
          workedOverlapItems.push(s2.id)
          // }
        }
      }
    }

    schedules.forEach((schedule, index) => {
      if (!rows[GSTC.api.GSTCID(schedule.userId)]) return
      let top = this.setTopPerTime(parseInt(schedule.startTime))
      const id = GSTC.api.GSTCID(schedule.id)
      if (schedule.isLeave) {
        items[id] = {
          id,
          label: schedule.type,
          rowId: GSTC.api.GSTCID(schedule.userId),
          // top: index * 10,
          style: {
            backgroundColor: '#d7d7d7',
            border: '2px dashed #b4b4b4',
            top:
              // schedule.startTime === '8' ? '5px' :
              top + 'px',
            zIndex: '999',
            color: '#000',
          },
          time: {
            start: new Date(schedule.startDate).getTime(),
            end: new Date(schedule.endDate).getTime(),
          },
          schedule,
          height: this.scheduleService.setHeightNewTask(schedule.hoursWorked),
          description: schedule.hoursWorked + 'h',
        }

        return
      }
      items[id] = {
        id,
        label: schedule.project[0]? schedule.project[0].name : "",
        rowId: GSTC.api.GSTCID(schedule.userId),
        style: {
          backgroundColor: schedule.teamLead[0].color
            ? `rgba(${schedule.teamLead[0].color}, ${workedOverlapItems.includes(schedule.id) ? '0.8' : '1'})`
            : 'rgba(17, 160, 255,.8)',
          border: 0,
          top: top + 'px',
        },
        time: {
          start: new Date(schedule.startDate).getTime(),
          end: new Date(schedule.endDate).getTime(),
        },
        schedule,
        height: this.scheduleService.setHeightNewTask(schedule.hoursWorked),
        description: schedule.hoursWorked + 'h',
      }
    })

    this.scheduleService.updateState('config', (config) => {
      config.list.rows = rows
      config.chart.items = items
      return config
    })
  }

  initRowsColumns2(team) {
    let users: any = []
    let schedulesConcat: any = []
    team.map((v) => {
      users = users.concat(v.members)
      if (v.schedules.length > 0)
        if (v.schedules[0].id) {
          schedulesConcat = schedulesConcat.concat(v.schedules)
        }
      return v
    })

    let us: any = []
    let usersNoTeam: any = {}
    team.forEach((t, i) => {
      let teamName = this.teamLeader.find((u) => u.id === t.id)?.name.toLowerCase()
      if (t.id) {
        us.push({
          id: 'group-' + (i + 1),
          label: teamName ? 'Team ' + teamName[0].toUpperCase() + teamName.slice(1) : 'No team',
          expanded: true,
          height: 20,
          classNames: ['team-highlight'],
        })
      }
      t.members.forEach((user: User) => {
        if (!user.teamLeadId) {
          usersNoTeam[user.id] = user.id
          return
        }
        let name = user.name.toLowerCase()
        let lastNmae = user.surname.toLowerCase()
        us.push({
          id: user.id,
          label: name[0].toUpperCase() + name.slice(1) + ' ' + lastNmae[0].toUpperCase() + lastNmae.slice(1),
          img: this.getParseInt(user.username)
            ? 'https://cdgisweb.cdg.co.th/telimage/PS' + user.username + '_01.jpg'
            : 'https://i.guim.co.uk/img/media/26392d05302e02f7bf4eb143bb84c8097d09144b/446_167_3683_2210/master/3683.jpg?width=1200&quality=85&auto=format&fit=max&s=a52bbe202f57ac0f5ff7f47166906403',
          availableHour: 40,
          expanded: false,
          position: user.position,
          height: 165,
          // parentId: 'group-' + (i + 1),
          user: user,
        })

        // "gstcid-641263ea9979540d2a81b9ef"
      })
    })
    users = us
    
    let schedules: any[] = []
    let workedOverlapItems: any[] = []
    for (let i = 0; i < schedulesConcat.length; i++) {
      let s1 = schedulesConcat[i]
      let s1Start = new Date(s1.startDate).getTime()
      let s1End = new Date(s1.endDate).getTime()
      for (let j = 1; j < schedulesConcat.length; j++) {
        let s2 = schedulesConcat[j]
        if (s1.id === s2.id) continue
        let s2Start = new Date(s2.startDate).getTime()
        let s2End = new Date(s2.endDate).getTime()

        let overlap
        if (s1.userId === s2.userId) {
             overlap =
            ((parseInt(s1.startTime) >= parseInt(s2.startTime) && parseInt(s1.startTime) < parseInt(s2.endTime)) ||
              (parseInt(s1.endTime) > parseInt(s2.startTime) && parseInt(s1.endTime) <= parseInt(s2.endTime))) &&
            ((s1Start >= s2Start && s1Start < s2End) || (s1End <= s2End && s1End > s2Start))
        }

        let start
        let end
        if (overlap) {
          start = s1Start > s2Start ? s1Start : s2Start
          end = s1End < s2End ? s1End : s2End
        
          workedOverlap.push({
            start,
            end,
            rowId: s1.userId,
          })
          workedOverlapItems.push(s1.id)
          workedOverlapItems.push(s2.id)
          // }
        }
      }
    }

    schedulesConcat.forEach((schedule, index) => {
      if (schedule.userId === usersNoTeam[schedule.userId]) return
      let top = this.setTopPerTime(parseInt(schedule.startTime))
      if (schedule.isLeave) {
        schedules = schedules.concat({
          id: schedule.id,
          label: schedule.type,
          rowId: schedule.userId,
          // top: index * 10,
          style: {
            backgroundColor: '#d7d7d7',
            border: '2px dashed #b4b4b4',
            top:
              // schedule.startTime === '8' ? '5px' :
              top + 'px',
            zIndex: '999',
            color: '#000',
          },
          time: {
            start: new Date(schedule.startDate).getTime(),
            end: new Date(schedule.endDate).getTime(),
          },
          schedule,
          height: this.scheduleService.setHeightNewTask(schedule.hoursWorked),
          description: schedule.hoursWorked + 'h',
        })
      }
      if (!schedule?.teamLead[0]) return

      schedules = schedules.concat({
        id: schedule.id,
        // label: schedule.name,
        label: schedule.project[0].name,
        rowId: schedule.userId,
        // top: index * 10,
        style: {
          backgroundColor: schedule.teamLead[0].color
            ? `rgba(${schedule.teamLead[0].color}, ${workedOverlapItems.includes(schedule.id) ? '0.8' : '1'})`
            : 'rgba(17, 160, 255,.8)',
          border: 0,
          top:
            // schedule.startTime === '8' ? '5px' :
            top + 'px',
        },
        time: {
          start: new Date(schedule.startDate).getTime(),
          end: new Date(schedule.endDate).getTime(),
        },
        schedule,
        height: this.scheduleService.setHeightNewTask(schedule.hoursWorked),
        description: schedule.hoursWorked + 'h',
      })
    })

    this.scheduleService.updateState('config', (config) => {
      config.list.rows = GSTC.api.fromArray(users)
      config.chart.items = GSTC.api.fromArray(schedules)
      return config
    })
    // this.users = users
    // this.schedules = schedules
  }

  setTopPerTime(t: number) {
    let time = t - 7
    let tiemHeight = 15
    let sum = tiemHeight * time + 5 * time - tiemHeight
    return t > 12 ? sum - 20 : sum
  }

  getParseInt(s: string) {
    let a = s.match(/^[0-9]+$/) != null
    return a
   
  }

  itemSelectOptions() {
    return {
      showOverlay: false,
      cells: false,
      multipleSelection: false,
      events: {
        onEnd: (selected) => {
          if (!selected) return selected
          if (selected['chart-timeline-items-row-item'].length === 1) {
            let selectedSchedule = selected['chart-timeline-items-row-item'][0]

            let user = this.scheduleService.getRow(selectedSchedule.rowId)
            this.scheduleService.itemSelected$ = {
              data: selectedSchedule,
              state: !selectedSchedule.schedule.isLeave ? 'edit' : 'leave',
              user,
              project: selectedSchedule.schedule.project[0],
            }
          }
          if (selected['chart-timeline-grid-row-cell'].length === 0) return selected
          let selectedCell = selected['chart-timeline-grid-row-cell']
          let startTimeSelected = selectedCell[0]?.time.leftGlobal
          let endTimeSelected = selectedCell[selectedCell.length - 1]?.time.rightGlobal

          selected['chart-timeline-grid-row-cell'] = []
          selected['chart-timeline-items-row-item'] = []
          return selected
        },
      },
      onSelecting: (selecting: EventSelection, last: EventSelection) => {
        // if (selecting['chart-timeline-grid-row-cell'].length > 0) {
        selecting['chart-timeline-grid-row-cell'] = []
        // // }
        // if (selecting['chart-timeline-grid-row-cell'].length === 1) {
        //   this.isSelectRow = selecting['chart-timeline-grid-row-cell'][0]['id'].split('-')[1]
        // }
        // selecting['chart-timeline-grid-row-cell'] = selecting['chart-timeline-grid-row-cell'].filter((value) => {
        //   return (
        //     value['id'].split('-')[1] === this.isSelectRow && ![6, 0].includes(value['time']['leftGlobalDate'].day())
        //   )
        // })
        return selecting
      },
    }
  }

  itemResizeOptions() {
    return {
      events: {
        onEnd: ({ items }) => {
          let itemsInitial = items.initial[0]
          let itemsAfter = items.after[0]
          let isWeekend = false
          let users = items.after.map((item) => {
            let start = [6, 0].includes(GSTC.api.date(item.time.start).day())
            let end = [6, 0].includes(GSTC.api.date(item.time.end).day())
            if (start || end) {
              isWeekend = true
              this.confirmationService.confirm({
                message: `Invalid work day ?`,
                header: 'Confirmation',
                acceptLabel: 'OK',
                rejectButtonStyleClass: 'accepBtnDisable',
              })
            }
            return {
              id: item.id.split('-')[1],
              inputStartDate: item.time.start.toString(),
              inputEndDate: item.time.end.toString(),
            }
          })
          if (isWeekend) return items.initial

          this.confirmationService.confirm({
            message: `Are you sure you want to change task ${itemsInitial.label} ?`,
            header: 'Confirmation',
            icon: 'pi pi-exclamation-triangle',
            accept: () => {
              this.scheduleService.updateDateSchedules({ userDates: users }).subscribe((res) => {
                this.messageService.add({ severity: 'success', summary: 'Confirmed', detail: 'Record deleted' })
              })
            },
            reject: (type) => {
              items.initial.forEach((item) => {
                this.scheduleService.updateState(`config.chart.items.${item.id}`, item)
              })
              switch (type) {
                case ConfirmEventType.REJECT:
                  this.messageService.add({ severity: 'info', summary: 'Rejected', detail: 'You have rejected' })
                  break
                case ConfirmEventType.CANCEL:
                  this.messageService.add({ severity: 'warn', summary: 'Cancelled', detail: 'You have cancelled' })
                  break
              }
            },
          })
          return items.after
        },
      },
    }
  }
}

"""

dotnet_example_code = """
using AtlasX.Engine.AppSettings;
using AtlasX.Engine.Connector;
using AtlasX.Engine.Connector.Services;
using AtlasX.Engine.Extensions;
using AtlasX.Web.Service.Core;
using AtlasX.Web.Service.Mail;
using AtlasX.Web.Service.Mail.Services;
using AtlasX.Web.Service.OAuth.Dto;
using AtlasX.Web.Service.OAuth.Models;
using AtlasX.Web.Service.OAuth.Repositories.Interfaces;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Options;
using Microsoft.IdentityModel.Tokens;
using Serilog;
using System;
using System.Globalization;
using System.IdentityModel.Tokens.Jwt;
using System.IO;
using System.Net.Http;
using System.Net.Mail;
using System.Text;
using System.Threading.Tasks;

namespace AtlasX.Web.Service.OAuth.Services
{

    public class AppAuthenService : IAppAuthenService
    {
        private readonly FacebookService _facebookService;
        private readonly HttpClient _httpClient;
        private readonly AppSettings _appSettings;
        private readonly IDbDataAccessService _dbDataAccessService;
        private readonly IAppMailService _appMailService;
        private Random _random = new Random();

        public AppAuthenService(
            IOptions<AppSettings> appSettings
            , IDbDataAccessService dbDataAccessService
            , IAppMailService appMailService
        )
        {
            _httpClient = new HttpClient();
            _facebookService = new FacebookService(_httpClient);

            _appSettings = appSettings.Value;
            _dbDataAccessService = dbDataAccessService;
            _appMailService = appMailService;
        }

        public IActionResult Authorization(ControllerBase controllerBase,
            IAuthorizationCodeRepository authorizationCodeRepository, IUserInfoRepository userInfoRepository,
            AuthorizeRequestDto model, IOAuth appSettingsOAuth)
        {
            if (string.IsNullOrWhiteSpace(model.RedirectUri)) // TODO: Validate uri from appsettings
            {
                return controllerBase.Content("invalid redirect_uri.");
            }

            if (model.ResponseType != "code")
            {
                return RedirectWithError(controllerBase, model.RedirectUri, model.State, "unsupported_response_type",
                    "The server does not support obtaining an authorization code using this method.");
            }

            if (model.CodeChallenge == null || model.CodeChallengeMethod != "S256")
            {
                return RedirectWithError(controllerBase, model.RedirectUri, model.State, "invalid_request",
                    "The request is missing a parameter, contains an invalid parameter, includes a parameter more than once, or is otherwise invalid.");
            }

            if (controllerBase.User.GetUserId() == -1)
            {
                return controllerBase.Unauthorized();
            }

            int userId = controllerBase.User.GetUserId();
            UserInfo userInfo = userInfoRepository.Get(userId);
            if (userInfo == null)
            {
                return controllerBase.Unauthorized();
            }

            string code = GenerateAuthenticationCode();
            string checksum = (code + userInfo.Username).GetSHA256HashString();
            authorizationCodeRepository.Add(
                model.CodeChallenge
                , model.CodeChallengeMethod
                , code
                , userId
                , appSettingsOAuth.AuthorizationCodeExpires
                , model.ClientId
                , model.RedirectUri
                , checksum
            );

            return controllerBase.Redirect($"{model.RedirectUri}#code={code}&state={model.State}");
        }

        public async Task<IActionResult> TokenAsync(ControllerBase controllerBase, IUserTokenRepository userTokenRepository,
            IUserInfoRepository userInfoRepository, IAuthorizationCodeRepository authorizationCodeRepository,
            TokenRequestDto model, IOAuth appSettingsOAuth, string codeVerifier)
        {
            switch (model.GrantType)
            {
                case "password":
                    return await RequestTokenByPasswordAsync(controllerBase, userTokenRepository, userInfoRepository,
                        appSettingsOAuth, model);
                case "refresh_token":
                    return RequestTokenByRefreshToken(controllerBase, userTokenRepository, userInfoRepository,
                        appSettingsOAuth, model);
                case "authorization_code":
                    {
                        if (!string.IsNullOrWhiteSpace(codeVerifier))
                        {
                            model.CodeVerifier = codeVerifier;
                        }

                        return RequestTokenByAuthorizationCode(controllerBase, userInfoRepository, authorizationCodeRepository,
                            userTokenRepository, appSettingsOAuth, model);
                    }
                default:
                    return controllerBase.BadRequest(new OAuthResponseErrorDto("unsupported_grant_type",
                        "The grant_type doesn't recognize."));
            }
        }

        private static string GenerateAccessToken(int userId, string clientId, string nonce, string secretKey,
            string issuer, int expiresAfter)
        {
            SymmetricSecurityKey key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(secretKey));
            SigningCredentials signingCredentials = new SigningCredentials(key, SecurityAlgorithms.HmacSha256);
            // var scope = "read write";

            JwtSecurityToken token = new JwtSecurityToken(
                issuer: issuer,
                audience: issuer,
                expires: DateTime.Now.AddSeconds(expiresAfter),
                signingCredentials: signingCredentials)
            {
                Payload =
            {
                ["sub"] = userId,
                ["cid"] = clientId,
                ["iat"] = DateTimeOffset.UtcNow.ToUnixTimeSeconds(),
                ["nonce"] = nonce
            }
            };

            // token.Payload["scope"] = scope;

            return new JwtSecurityTokenHandler().WriteToken(token);
        }

        private static string GenerateRefreshToken()
        {
            string token = Guid.NewGuid().ToString("n");
            return token;
        }

        private static string GenerateNonce()
        {
            string nonce = Guid.NewGuid().ToString("n");
            return nonce;
        }

        private static string GenerateAuthenticationCode()
        {
            string code = Guid.NewGuid().ToString("n");
            return code;
        }

        private static IActionResult RedirectWithError(ControllerBase controllerBase, string redirectUri, string state,
            string error, string errorDescription)
        {
            string url = $"{redirectUri}?error={error}&error_description={errorDescription}&state={state}";
            return controllerBase.Redirect(url);
        }

        private async Task<IActionResult> RequestTokenByPasswordAsync(ControllerBase controllerBase,
            IUserTokenRepository userTokenRepository, IUserInfoRepository userInfoRepository, IOAuth appSettingsOAuth,
            TokenRequestDto model)
        {
            UserInfo userInfo;

            if (model.Source == 0) // Default: Username & Password
            {
                if (model.Username == null || model.Password == null)
                {
                    return controllerBase.BadRequest(new OAuthResponseErrorDto("invalid_request",
                        "The request is missing a required parameter."));
                }

                userInfo = userInfoRepository.Get(model.Username, model.Password, null);
            }
            else if (model.Source == 3) // Facebook: FacebookAccessToken (model.Password)
            {
                if (model.Password == null)
                {
                    return controllerBase.BadRequest(new OAuthResponseErrorDto("invalid_request",
                        "The request is missing a required parameter."));
                }

                FacebookUserProfileResponseDto facebookResult = await _facebookService.GetFacebookUserAsync(model.Password);

                if (facebookResult.Error != null)
                {
                    return controllerBase.BadRequest(new OAuthResponseErrorDto("invalid_grant",
                        facebookResult.Error.Message));
                }

                userInfo = userInfoRepository.Get(facebookResult.Id);

                if (userInfo == null)
                {
                    return controllerBase.BadRequest(new OAuthResponseErrorDto("invalid_grant", "User not found."));
                }

                if (model.Source != userInfo.Source)
                {
                    return controllerBase.BadRequest(new OAuthResponseErrorDto("invalid_grant",
                        "The user has not signed up yet."));
                }
            }
            else
            {
                return controllerBase.BadRequest(new OAuthResponseErrorDto("invalid_request", "The source not support."));
            }

            if (userInfo == null)
            {
                return controllerBase.BadRequest(new OAuthResponseErrorDto("invalid_grant",
                    "The username or password is incorrect."));
            }

            int userId = userInfo.Id;
            string clientId = model.ClientId;

            switch (appSettingsOAuth.Strategy)
            {
                case RefreshTokenStrategy.First when userTokenRepository.IsAlive(userId):
                    return controllerBase.Unauthorized(new OAuthResponseErrorDto("invalid_grant",
                        "The user logon already exists."));
                case RefreshTokenStrategy.Last:
                    userTokenRepository.Remove(userId);
                    break;
                case RefreshTokenStrategy.Multiple:
                    break;
                default:
                    throw new ArgumentOutOfRangeException();
            }

            return controllerBase.Ok(GenerateAccessTokenResponse(userTokenRepository, appSettingsOAuth, userId, clientId,
                userInfo.Username));
        }

        private static IActionResult RequestTokenByAuthorizationCode(ControllerBase controllerBase,
            IUserInfoRepository userInfoRepository, IAuthorizationCodeRepository authorizationCodeRepository,
            IUserTokenRepository userTokenRepository, IOAuth appSettingsOAuth, TokenRequestDto model)
        {
            if (model.Code == null || model.CodeVerifier == null)
            {
                return controllerBase.BadRequest(new OAuthResponseErrorDto("invalid_request",
                    "The request is missing a required parameter, includes an unsupported parameter value (other than grant type)."));
            }

            string code = model.Code;
            AuthorizationCode authorizationCode = authorizationCodeRepository.Get(code);

            if (authorizationCode == null)
            {
                return controllerBase.BadRequest(new OAuthResponseErrorDto("invalid_grant",
                    "Invalid authorization_code or expired."));
            }

            if (authorizationCode.Expires.CompareTo(DateTime.Now) < 0)
            {
                return controllerBase.BadRequest(new OAuthResponseErrorDto("invalid_grant",
                    "The authorization_code has expired."));
            }

            if (authorizationCode.RedirectUri != model.RedirectUri)
            {
                return controllerBase.BadRequest(new OAuthResponseErrorDto("invalid_grant", "Invalid redirect_uri."));
            }

            if (authorizationCode.CodeChallenge != model.CodeVerifier.GetSHA256HashString())
            {
                return controllerBase.BadRequest(new OAuthResponseErrorDto("invalid_grant", "Invalid code_challenge."));
            }

            int userId = authorizationCode.UserId;
            UserInfo userInfo = userInfoRepository.Get(userId);

            if (userInfo == null)
            {
                return controllerBase.Unauthorized();
            }

            if (authorizationCode.CheckSum != (authorizationCode.Code + userInfo.Username).GetSHA256HashString())
            {
                return controllerBase.BadRequest(new OAuthResponseErrorDto("invalid_grant", "Invalid authorization_code."));
            }

            string clientId = model.ClientId;


            switch (appSettingsOAuth.Strategy)
            {
                case RefreshTokenStrategy.First when userTokenRepository.IsAlive(userId):
                    return controllerBase.Unauthorized(new OAuthResponseErrorDto("invalid_grant",
                        "The user logon already exists."));
                case RefreshTokenStrategy.Last:
                    userTokenRepository.Remove(userId);
                    break;
                case RefreshTokenStrategy.Multiple:
                    break;
                default:
                    throw new ArgumentOutOfRangeException();
            }

            AccessTokenResponseDto accessTokenResponse = GenerateAccessTokenResponse(userTokenRepository, appSettingsOAuth,
                userId, clientId, userInfo.Username);

            authorizationCodeRepository.Remove(code);
            authorizationCodeRepository.RemoveExpired();

            return controllerBase.Ok(accessTokenResponse);
        }

        private static IActionResult RequestTokenByRefreshToken(ControllerBase controllerBase,
            IUserTokenRepository userTokenRepository, IUserInfoRepository userInfoRepository, IOAuth appSettingsOAuth,
            TokenRequestDto model)
        {
            if (model.RefreshToken == null)
            {
                return controllerBase.BadRequest(new OAuthResponseErrorDto("invalid_request",
                    "The request is missing a required parameter, includes an unsupported parameter value (other than grant type)."));
            }

            UserToken existsRefreshToken = userTokenRepository.Get(refreshToken: model.RefreshToken);
            if (existsRefreshToken == null)
            {
                return controllerBase.BadRequest(new OAuthResponseErrorDto("invalid_grant",
                    "Invalid refresh_token or expired."));
            }

            string password = userInfoRepository.Get(existsRefreshToken.UserId).Username;
            if (existsRefreshToken.CheckSum != (existsRefreshToken.RefreshToken + password).GetSHA256HashString())
            {
                return controllerBase.BadRequest(new OAuthResponseErrorDto("invalid_grant", "Invalid refresh_token."));
            }

            if (existsRefreshToken.Expires.CompareTo(DateTime.Now) < 0)
            {
                return controllerBase.BadRequest(new OAuthResponseErrorDto("invalid_grant",
                    "The refresh_token has expired."));
            }

            // Remove old refresh token.
            userTokenRepository.Remove(model.RefreshToken);

            return controllerBase.Ok(GenerateAccessTokenResponse(userTokenRepository, appSettingsOAuth,
                existsRefreshToken.UserId, existsRefreshToken.ClientId, password));
        }

        private static AccessTokenResponseDto GenerateAccessTokenResponse(IUserTokenRepository userTokenRepository,
            IOAuth appSettingsOAuth, int userId, string clientId, string username)
        {
            string nonce = GenerateNonce();
            string accessToken = GenerateAccessToken(
                userId: userId,
                clientId: clientId,
                nonce: nonce,
                secretKey: appSettingsOAuth.SecretKey,
                issuer: appSettingsOAuth.Issuer,
                expiresAfter: appSettingsOAuth.AccessTokenExpires);
            string refreshToken = GenerateRefreshToken();
            string checksum = (refreshToken + username).GetSHA256HashString();
            userTokenRepository.Add(refreshToken, userId, clientId, nonce, appSettingsOAuth.RefreshTokenExpires, checksum);
            userTokenRepository.RemoveExpired();

            return new AccessTokenResponseDto
            {
                AccessToken = accessToken,
                TokenType = "bearer",
                ExpiresIn = appSettingsOAuth.AccessTokenExpires,
                RefreshToken = refreshToken
            };
        }

        public bool Verify(VerifyRequestDto verifyRequest)
        {
            VerifyCode verifyCode = GenerateVerifyCode();

            return SaveVerifyCode(verifyRequest, verifyCode)
                   && DeliveryVerifyCode(verifyRequest, verifyCode);
        }

        public VerifyCode GenerateVerifyCode()
        {
            // Generate code.
            string code = _random.Next(000000, 999999).ToString("D6");

            // Create expired from configure.
            // Default expired is 5 minutes.
            DateTime expired = DateTime.Now;
            int expiresInMinutes = _appSettings.OAuth.VerifyCodeExpires > 0
                ? _appSettings.OAuth.VerifyCodeExpires / 60
                : 5;
            expired = expired.AddMinutes(expiresInMinutes);

            return new VerifyCode
            {
                Code = code,
                Expires = expired,
                Age = expiresInMinutes
            };
        }

        public bool IdentityExisting(VerifyType verifyType, string identity)
        {
            string verifyTypeParam = verifyType == VerifyType.email ? "EMAIL" : "TELEPHONE";

            QueryParameter queryParameter = new QueryParameter();
            queryParameter.Add(_appSettings.Database.ProcedureParameter, "APP_USER_EXISTS_Q");
            queryParameter.Add(verifyTypeParam, identity);

            QueryResult queryResult = _dbDataAccessService.ExecuteProcedure(queryParameter);
            if (queryResult.Success)
            {
                return queryResult.Total > 0;
            }
            else
            {
                Log.Error($"File: AppAuthenService.cs; Function: IdentityExisting; Detail: ${queryResult.Message}");
                return false;
            }
        }

        private bool SaveVerifyCode(VerifyRequestDto verifyRequest, VerifyCode verifyCode)
        {
            QueryParameter queryParameter = new QueryParameter();
            queryParameter.Add(_appSettings.Database.ProcedureParameter, "APP_CONFIRM_CODE_I");
            queryParameter.Add("IDENTITY", verifyRequest.Email);
            queryParameter.Add("CODE", verifyCode.Code);
            queryParameter.Add("EXPIRE_TIME", verifyCode.Expires.ToUnixTimeMilliseconds());
            queryParameter.Add("ACTION", verifyRequest.Action);
            queryParameter.Add("TYPE", verifyRequest.VerifyWith);

            return _dbDataAccessService
                .ExecuteProcedure(queryParameter)
                .Success;
        }

        private bool DeliveryVerifyCode(VerifyRequestDto verifyRequest, VerifyCode verifyCode)
        {
            if (verifyRequest.VerifyWith == VerifyType.email)
            {
                MailMessage mailMessage = new MailMessage();
                mailMessage.Sender = _appSettings.Email.SenderAddress.ToMailAddress();
                mailMessage.From = _appSettings.Email.SenderAddress.ToMailAddress();
                mailMessage.To.Add(verifyRequest.Email.ToMailAddress());
                mailMessage.Subject = "[SYSTEM/APP] กรุณายืนยันอีเมลของคุณ";
                mailMessage.SubjectEncoding = Encoding.UTF8;

                string templateName = verifyRequest.Action == VerifyAction.register
                    ? "register.html"
                    : "forget-password.html";
                string templatePath = Path.Join(Directory.GetCurrentDirectory(), "OAuth", "Assets", "Verify", templateName);
                string mailBodyTemplate = File.ReadAllText(templatePath);
                CultureInfo cultureInfo = CultureInfo.CreateSpecificCulture("th-TH");

                mailMessage.Body = mailBodyTemplate
                    .Replace("{EMAIL}", verifyRequest.Email)
                    .Replace("{CODE}", verifyCode.Code)
                    .Replace("{AGE}", verifyCode.Age.ToString())
                    .Replace("{EXPIRED}",
                        $"{verifyCode.Expires.ToString("d MMMM yyyy", cultureInfo)} เวลา {verifyCode.Expires.ToLongTimeString()} น.");
                mailMessage.BodyEncoding = Encoding.UTF8;
                mailMessage.IsBodyHtml = true;
                mailMessage.Priority = MailPriority.Normal;

                return _appMailService.Send(mailMessage);
            }
            else
            {
                // TO DO: Implement send message api(OTP).
                // ...

                throw new NotImplementedException();
            }
        }
    }
}

"""
