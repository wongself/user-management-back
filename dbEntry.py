from dbAccess import UserAccess, OrderAccess, AnalysisAccess
import settings

userAC = UserAccess(host=settings.dbHost,
                    port=settings.dbPort,
                    user=settings.dbUser,
                    pwd=settings.dbPwd,
                    dbName=settings.dbCol,
                    docName=settings.dbColUser)

orderAC = OrderAccess(host=settings.dbHost,
                      port=settings.dbPort,
                      user=settings.dbUser,
                      pwd=settings.dbPwd,
                      dbName=settings.dbCol,
                      docName=settings.dbColOrder)

analysisAC = AnalysisAccess(host=settings.dbHost,
                            port=settings.dbPort,
                            user=settings.dbUser,
                            pwd=settings.dbPwd,
                            dbName=settings.dbCol,
                            docName=settings.dbColAnalysis)
